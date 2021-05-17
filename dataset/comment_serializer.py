from django.contrib.auth.models import User
from api.models import CommentLabel

field_translation = {
    "HATEFUL": "HATEFUL",
    "CALLS": "CALLS",
    "MUJER": "WOMEN",
    "LGBTI": "LGBTI",
    "RACISMO": "RACISM",
    "POBREZA": "CLASS",
    "POLITICA": "POLITICS",
    "DISCAPACIDAD": "DISABLED",
    "ASPECTO": "APPEARANCE",
    "CRIMINAL": "CRIMINAL"
}

field_mapping = {
    "HATEFUL": "is_hateful",
    "CALLS": "calls_for_action",
}

for name_spanish, name_english in field_translation.items():
    if name_english not in field_mapping:
        field_mapping[name_english] = CommentLabel.type_mapping[name_spanish]


hate_categories = [x for x in field_mapping.keys() if x not in ['HATEFUL', 'CALLS']]

def ignore_label(comment_label):
    """
    Tenemos que ignorar esta etiqueta?

    Ignoramos si usó "OTROS" y nada más
    """
    characteristics = {
        key:getattr(comment_label, field_mapping[key]) for key in hate_categories
    }
    return comment_label.is_hateful and all(not v for v in characteristics.values())

class CommentSerializer:
    """
    This is our serializer for
    """

    def __init__(self, annotators=None, anonymize=True, raw=False):
        """
        Constructor

        Arguments:
        ----------

        annotators: list[str]
            List of annotators

        anonymize: bool (default True)
            Remove tweet ids

        raw: bool (default False)
            Returns only the annotations without assignation
        """
        if annotators:
            self.annotators = annotators
        else:
            self.annotators = User.objects.exclude(article_labels=None).order_by('username')

        self.anonymized_names = {
            user.username: f"annotator_{i+1}"
            for i, user in enumerate(self.annotators)
        }

        self.ignored_labels = 0
        self.anonymize = anonymize
        self.anonymize_annotator = True
        self.raw = raw

    def assign(self, raw_comment):
        """
        Process raw comment
        """
        ret = raw_comment.copy()
        ret["HATEFUL"] = int(len(raw_comment['HATEFUL']) >= 2)

        for cat in hate_categories + ["CALLS"]:
            ret[cat] = 0

        if ret["HATEFUL"]:
            ret["CALLS"] = int(len(raw_comment['CALLS']) >= 2)

            for category in hate_categories:
                ret[category] = int(len(raw_comment[category]) > 0)

        return ret

    def serialize(self, comment):
        """
        Serialize comment
        """
        article = comment.article
        ret = {
            **{
                "id": comment.id,
                "text": comment.text,
                "article_id": str(article.tweet_id),
                "annotators": [],
            },
            **{key:[] for key in field_mapping}
        }

        if not self.anonymize:
            ret["tweet_id"] = str(comment.tweet_id)

        for label in comment.labels.prefetch_related('article_label', 'article_label__user').all():
            username = label.article_label.user.username

            if self.anonymize or self.anonymize_annotator:
                annotator_name = self.anonymized_names[username]
            else:
                annotator_name = username

            ret["annotators"].append(annotator_name)

            if ignore_label(label):
                self.ignored_labels += 1
                continue

            for name, field in field_mapping.items():
                # Si es verdadero, agregamos
                if getattr(label, field):
                    ret[name].append(annotator_name)

        if not self.raw:
            return self.assign(ret)
        return ret
