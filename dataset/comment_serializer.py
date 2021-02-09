from django.contrib.auth.models import User
from api.models import CommentLabel

field_translation = {
    "HATE": "HATE",
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
    "HATE": "is_hateful",
    "CALLS": "calls_for_action",
}

for name_spanish, name_english in field_translation.items():
    if name_english not in field_mapping:
        field_mapping[name_english] = CommentLabel.type_mapping[name_spanish]

def ignore_label(comment_label):
    """
    Tenemos que ignorar esta etiqueta?

    Ignoramos si usó "OTROS" y nada más
    """
    return comment_label.is_hateful and all(
        not getattr(comment_label, field) for key, field in field_mapping.items()
        if key not in {"HATE", "CALLS"}
    )

class CommentSerializer:
    """
    This is our serializer for
    """

    def __init__(self, annotators=None, anonymize=True):
        """
        Constructor
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

    def serialize(self, comment):
        """
        Serialize comment
        """
        article = comment.article
        ret = {
            **{
                "id": comment.id,
                "text": comment.text,
                "article_id": article.tweet_id,
                "annotators": [],
            },
            **{key:[] for key in field_mapping}
        }

        if not self.anonymize:
            ret["tweet_id"] = comment.tweet_id

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

        return ret
