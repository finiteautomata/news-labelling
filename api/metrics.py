from collections import defaultdict
import pandas as pd
import numpy as np
import krippendorff
from api.models import ArticleLabel, CommentLabel


def no_null_columns(df):
    """
    Return dataframe only having those columns for which no nan appears
    """
    return df[df.columns[df.notna().all()]]

class AgreementCalculator:
    """
    Class that calculates agreement metrics
    """

    def __get_labels(self, batch, articles, users):
        """
        Get articles from options
        """
        query = {}
        if batch:
            # We take all labels for articles in batch
            query["article__in"] =  batch.articles.all()

        elif articles:
            query["article__in"] =  articles

        if users:
            self.users = users
            query["user__in"] = users

        self.article_labels = list(ArticleLabel.objects.filter(**query).prefetch_related(
            'comment_labels', 'comment_labels__comment', 'article', 'user'
        ))
        self.article_to_comments = defaultdict(list)
        self.comment_text = {}

        for article_label in self.article_labels:
            for comment_label in article_label.comment_labels.all():
                comment = comment_label.comment
                self.comment_text[comment.id] = comment.text
                self.article_to_comments[comment.article_id].append(comment)

        if not self.users:
            self.users = list({label.user for label in self.article_labels})

    def __init__(self, batch=None, articles=None, users=None):
        """
        Constructor
        """

        if all(opt is None for opt in [batch, articles, users]):
            raise ValueError("Must bring batch, articles or users")

        self.__get_labels(
            batch=batch, articles=articles, users=users
        )

        self.df_comments = None

    @property
    def usernames(self):
        return sorted(user.username for user in self.users)



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

        if self.df_comments is None:
            keys = ["HATE", "CALLS"]+ list(CommentLabel.type_mapping)
            idx = pd.MultiIndex.from_product(
                [keys, self.usernames],
                names=["categoria", "etiquetador"]
            )

            self.df_comments = pd.DataFrame(index=idx)

            for article_label in self.article_labels:
                username = article_label.user.username
                for comment_label in article_label.comment_labels.all():
                    """
                    Seteo odio primero
                    """
                    self.df_comments.loc[("HATE", username), comment_label.comment_id] = comment_label.is_hateful
                    self.df_comments.loc[("CALLS", username), comment_label.comment_id] = comment_label.calls_for_action

                    for name, field in CommentLabel.type_mapping.items():
                        val = getattr(comment_label, field)
                        self.df_comments.loc[(name, username), comment_label.comment_id] = val
        if on:
            return self.df_comments.loc[on.upper()]
        else:
            return self.df_comments

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
        any_marked_positive = df.fillna(0).sum() > 0
        support = any_marked_positive.sum()
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

        return df.fillna(0).sum(axis=1) / support


    def get_category_report(self, category):
        """
        Returns category report
        """
        category_df = self.get_labelled_comments(category)
        category_df = no_null_columns(category_df)

        alpha, support = self.get_agreement(category)

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
            # Sort comments by positive votes
            yield (article, triplet_comments)
