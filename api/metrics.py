import os
from collections import defaultdict
from django.contrib.auth.models import User
import pickle
from tqdm.auto import tqdm
import pandas as pd
import numpy as np
import krippendorff
from api.models import ArticleLabel, CommentLabel, Comment, comment


def no_null_columns(df):
    """
    Return dataframe only having those columns for which no nan appears
    """
    return df[df.columns[df.notna().all()]]

dir_path = os.path.dirname(os.path.abspath(__file__))
path_to_df = os.path.join(
    dir_path,
    "..",
    "data/dataframe_comments.pkl"
)
class DataFrameCalculator:
    """
    Object that calculates dataframe for comments and users annotation
    """
    def __init__(self):
        """
        Constructor
        """
        annotators = User.objects.exclude(assignment=None)

        self.usernames = [u.username for u in annotators]
        self.df_comments = None
        self.last_label_date = None

        if os.path.exists(path_to_df):
            try:
                with open(path_to_df, "rb") as f:
                    self.df_comments, self.last_label_date = pickle.load(f)

                self._update_df()
            except Exception as e:
                # Some error, forget about it!
                pass

        if self.df_comments is None:
            self._build_from_scratch()

    def _update_df(self):
        """
        Update dataframe
        """
        article_labels = ArticleLabel.objects.prefetch_related(
            'comment_labels', 'comment_labels__comment', 'user'
        ).filter(updated_at__gt=self.last_label_date)
        if article_labels.count() > 0:
            self.__update_with_labels(article_labels)
            self.save()

    def _build_from_scratch(self):
        """
        Build DF from scratch
        """
        keys = ["HATE", "CALLS"]+ list(CommentLabel.type_mapping)
        comments = Comment.objects.exclude(labels=None).only()

        idx = pd.MultiIndex.from_product(
            [keys, self.usernames],
            names=["categoria", "etiquetador"]
        )

        self.df_comments = pd.DataFrame(index=idx, columns=[c.id for c in comments])
        article_labels = ArticleLabel.objects.prefetch_related(
            'comment_labels', 'comment_labels__comment', 'user'
        )
        self.__update_with_labels(article_labels)
        self.save()

    def save(self):
        """
        Save dataframe
        """
        if self.df_comments is None or not self.last_label_date:
            raise ValueError("Date and DF must be not null")
        with open(path_to_df, "wb") as f:
            pickle.dump((self.df_comments, self.last_label_date), f)

    def preprocess_comment_label(self, comment_label):
        """
        Sacar 'OTROS'
        """

        if comment_label.is_hateful and comment_label.against_others:
            """
            Si no hay ningún otroflag => sacamos
            """
            comment_label.against_others = False

            if not any(
                getattr(comment_label, field)
                for k, field in CommentLabel.type_mapping.items()
            ):
                comment_label.is_hateful = False
                comment_label.calls_for_action = False


        return comment_label

    def __update_with_labels(self, article_labels):
        max_date = None
        for article_label in tqdm(article_labels, total=article_labels.count()):
            username = article_label.user.username
            if not max_date:
                max_date = article_label.updated_at
            else:
                max_date = max(max_date, article_label.updated_at)

            for comment_label in article_label.comment_labels.all():
                """
                Seteo odio primero
                """
                comment_label = self.preprocess_comment_label(comment_label)

                self.df_comments.loc[("HATE", username), comment_label.comment_id] = comment_label.is_hateful
                self.df_comments.loc[("CALLS", username), comment_label.comment_id] = comment_label.calls_for_action

                for name, field in CommentLabel.type_mapping.items():
                    val = getattr(comment_label, field)
                    self.df_comments.loc[(name, username), comment_label.comment_id] = val

        self.last_label_date = max_date

    def get_df(self):
        """
        Get full dataframe
        """
        return self.df_comments

class AgreementCalculator:
    """
    Class that calculates agreement metrics
    """


    def __init__(self, batch=None, articles=None, comment_ids=None, users=None):
        """
        Constructor
        """

        if all(opt is None for opt in [batch, articles, users, comment_ids]):
            raise ValueError("Must bring batch, articles, comments or users")

        self.article_labels = ArticleLabel.objects.prefetch_related(
                'comment_labels', 'comment_labels__comment', 'user'
        )
        self.users = None
        self.comment_ids = None

        if batch:
            # We take all labels for articles in batch
            self.comment_ids = [c.id for c in Comment.objects.filter(article__batch=batch)]
            self.article_labels = self.article_labels.filter(article__batch=batch)

        elif articles:
            self.comment_ids = [c.id for c in Comment.objects.filter(article__in=articles)]
            self.article_labels = self.article_labels.filter(article__in=articles)
        elif comment_ids:
            self.comment_ids = comment_ids
        if users:
            self.users = users
            self.article_labels = self.article_labels.filter(user__in=users)
        self.dataframe_calculator = DataFrameCalculator()

    @property
    def usernames(self):
        return sorted(user.username for user in self.users)

    @property
    def keys(self):
        """
        Return analysis keys
        """
        return ["HATE", "CALLS"]+ list(CommentLabel.type_mapping)

    def get_labelled_articles(self):
        """
        Labelled articles

        1 means it labelled the article
        0 means it was skipped
        NaN not labelled
        """
        df = pd.DataFrame({"name":self.usernames})
        df.set_index("name", inplace=True)

        for label in self.article_labels:
            username = label.user.username
            df.loc[username, label.article.title] = int(label.is_interesting)

        return df

    def get_labelled_comments(self, on=None):
        """
        Get labelled comments
        1 means labelled as hateful, 0 as not. NaN not labelled

        """
        ret = self.dataframe_calculator.get_df()
        if on:
            ret = ret.loc[on.upper()]

            if self.users:
                ret = ret.loc[[u.username for u in self.users]]

        if self.comment_ids:
            ret = ret[ret.columns.intersection(self.comment_ids)]
        return ret



    def get_agreement(self, on="HATE", users=None):
        """
        Get agreement

        Arguments:
        ---------

           on: "string"

           Must be one of
            - hate
            - MUJER
            - LGBTI
            - RACISMO
            - POBREZA
            - DISCAPACIDAD
            - POLITICA
            - ASPECTO
            - CRIMINAL
            - OTROS

        """
        df = self.get_labelled_comments(on)

        if users:
            df = df.loc[users]
        """
        Get support
        """

        #labelled_by_all = df.columns[df.notna().all()]
        #any_marked_positive = df[labelled_by_all].sum() > 0
        any_marked_positive = (df > 0).sum()
        support = (any_marked_positive > 0).sum()
        if support == 0:
            return np.nan, support

        return krippendorff.alpha(df.values.astype('float')), support

    def get_bias_towards(self, on="hate"):
        """
        Get bias towards positive class

        Arguments:
        ---------

           on: "string"

           Must be one of
            - hate
            - MUJER
            - LGBTI
            - RACISMO
            - POBREZA
            - DISCAPACIDAD
            - POLITICA
            - ASPECTO
            - CRIMINAL
            - OTROS

        """
        df = self.get_labelled_comments(on)

        support = df.notna().sum(axis=1)

        return df.sum(axis=1, skipna=True) / support

    def get_bias_all(self, zscore=False):
        """
        Get bias towards all classes
        """
        keys = [k for k in self.keys if k != "OTROS"]
        df = pd.DataFrame(index=keys, columns=self.usernames)

        for key in keys:
            agrees = self.get_bias_towards(key)
            #for user in users:
            #    df.loc[key, user.username] = agrees[user.username]
            df.loc[key] = agrees

        if zscore:
            mean = df.mean(axis=1)
            std = df.std(axis=1)
            df = df.subtract(mean, axis=0)
            df = df.divide(std, axis=0)
        return df.fillna(0)

    def get_category_report(self, category):
        """
        Returns category report
        """
        category_df = self.get_labelled_comments(category)
        category_df = no_null_columns(category_df)

        alpha, support = self.get_agreement(category)
        # Got agreement

        report = CategoryReport(category, list(category_df.index), alpha, support)

        agree_comments = category_df[category_df.columns[category_df.all()]]
        #non_hateful_comments = category_df[category_df.columns[(~category_df.astype(bool)).all()]]
        no_agree = ~((category_df.sum() == 0) | (category_df.sum() == len(self.users)))
        disagree_comments = category_df[category_df.columns[no_agree]]

        checked_articles = set()
        for article_label in self.article_labels:
            article = article_label.article
            if article.id in checked_articles:
                """
                Don't check things twice
                """
                continue
            else:
                checked_articles.add(article.id)

            for comment_label in article_label.comment_labels.all():
                comment = comment_label.comment
                if comment.id in agree_comments.columns:
                    report.agree_on(article, comment)
                elif comment.id in disagree_comments.columns:
                    # Annotators who said yes, this is hateful
                    positive_annotators = disagree_comments.index[disagree_comments[comment.id]]
                    negative_annotators = disagree_comments.index.difference(positive_annotators)

                    report.disagree_on(
                        article,
                        comment,
                        positive=positive_annotators,
                        negative=negative_annotators,
                    )
        return report

class CategoryReport:
    """
    Full report for a category and a group of articles

    This is terribly designed. Refactor if possible
    """

    def __init__(self, category, annotators, alpha, support):
        self.category = category
        self.alpha = alpha
        self.support = support
        self.annotators = annotators
        # Dicts from articles to agree comments
        self.article_to_agree = defaultdict(list)
        self.article_to_disagree = defaultdict(dict)

        self.num_agrees = 0
        self.num_disagrees = 0

    def agree_on(self, article, comment):
        """
        Mark agree on comment
        """
        self.num_agrees += 1
        self.article_to_agree[article].append(comment)

    def disagree_on(self, article, comment, positive, negative):
        """
        Mark disagree on comment
        """
        self.num_disagrees += 1
        self.article_to_disagree[article][comment] = {
            "positive": positive,
            "negative": negative
        }

    def agrees(self):
        """
        Generator for agree comments
        """
        for article, comments in self.article_to_agree.items():
            yield (article, comments)

    def disagrees(self):
        """
        Generator for disagree comments
        """
        for article, comment_votes in self.article_to_disagree.items():

            triplet_comments = [
                (comment, list(votes["positive"]), list(votes["negative"]))
                for comment, votes in comment_votes.items()
            ]

            triplet_comments = sorted(triplet_comments, key=lambda x: len(x[1]))
            # Sort comments by positive votes
            yield (article, triplet_comments)
