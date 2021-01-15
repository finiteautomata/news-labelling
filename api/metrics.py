import pandas as pd
import numpy as np
import krippendorff
from api.models import ArticleLabel, CommentLabel

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

        self.article_labels = ArticleLabel.objects.filter(**query)

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
            keys = ["HATE"] + list(CommentLabel.type_mapping)
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

                    for name, field in CommentLabel.type_mapping.items():
                        val = getattr(comment_label, field)
                        self.df_comments.loc[(name, username), comment_label.comment_id] = val
        if on:
            return self.df_comments.loc[on.upper()]
        else:
            return self.df_comments

    def get_agreement(self, on="HATE"):
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

        """
        Get support
        """

        labelled_by_all = df.columns[df.notna().all()]
        any_marked_positive = df[labelled_by_all].sum() > 0
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