from django.db import models
from .comment import Comment
from .article_label import ArticleLabel


class CommentLabel(models.Model):
    """
    Comment Label class:

    This represents a labelling from a user of a specific
    """
    HATE_SPEECH_TYPES = [
        ('MUJER', 'Sexo (mujeres)'),
        ('LGBTI', 'Identidad de género u orientación sexual'),
        ('RACISMO', 'Racismo, xenofobia, religión, lengua, país de origen'),
        ('POBREZA', 'Pobreza, situación socioeconómica, barrio de residencia'),
        ('DISCAPACIDAD', 'Discapacidad, problema de salud mental o adicciones'),
        ('POLITICA', 'Opinión o ideología política'),
        ('ASPECTO', 'Edad o aspecto físico (gordofobia)'),
        ('CRIMINAL', 'Situación penal, antecedentes, o privación de la libertad'),
        ('OTROS', 'Otros')
    ]

    type_mapping = {
        "MUJER": "against_women",
        "LGBTI": "against_lgbti",
        "RACISMO": "against_race",
        "POBREZA": "against_poor",
        "POLITICA": "against_political",
        "DISCAPACIDAD": "against_disabled",
        "ASPECTO": "against_aspect",
        "CRIMINAL": "against_criminals",
        "OTROS": "against_others",
    }

    inverse_type_mapping = {v:k for k, v in type_mapping.items()}

    is_hateful = models.BooleanField(blank=False, null=False)
    calls_for_action = models.BooleanField(blank=False, null=False)

    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="labels"
    )
    article_label = models.ForeignKey(
        ArticleLabel, on_delete=models.CASCADE, related_name="comment_labels"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    against_women = models.BooleanField(default=False)
    against_lgbti = models.BooleanField(default=False)
    against_race = models.BooleanField(default=False)
    against_poor = models.BooleanField(default=False)
    against_political = models.BooleanField(default=False)
    against_disabled = models.BooleanField(default=False)
    against_aspect = models.BooleanField(default=False)
    against_criminals = models.BooleanField(default=False)
    against_others = models.BooleanField(default=False)

    def hateful_against(self):
        """
        Returns hateful against communities
        """
        return [t for t, field in CommentLabel.type_mapping.items() if getattr(self, field)]

    def labels(self):
        """
        Returns all labels
        """
        if self.is_hateful:
            ret = ["HATE"]
            if self.calls_for_action:
                ret.append("CALLS")

            ret += self.hateful_against()

            return ret
        return []


    def __repr__(self):
        """
        Representation
        """
        user = self.article_label.user
        article = self.article_label.article
        ret = f"{user.username} sobre '{self.comment.text}'\n"
        if self.is_hateful:
            if self.calls_for_action:
                calls = " y violento "
            else:
                calls = " "

            ret += f"Odioso{calls} -> {self.hateful_against()}"
        else:
            ret += "No odioso"
        return ret

    def __str__(self):
        """
        String representation
        """
        return self.__repr__()
