from django.db import models
from .comment import Comment
from .article_label import ArticleLabel


class CommentLabel(models.Model):
    """
    Comment Label class:

    This represents a labelling from a user of a specific
    """
    HATE_SPEECH_TYPES = [
        ('MUJER', 'Violencia contra las mujeres'),
        ('LGBTI', 'Identidad de género u orientación sexual'),
        ('RACISMO', 'Racismo o xenofobia'),
        ('POBREZA', 'Pobreza, situación socioeconómica, barrio de residencia'),
        ('RELIGION', 'Religión'),
        ('DISCAPACIDAD', 'Discapacidad o Salud Mental'),
    ]

    type_mapping = {
        "MUJER": "against_women",
        "LGBTI": "against_lgbti",
        "RACISMO": "against_race",
        "POBREZA": "against_poor",
        "RELIGION": "against_religion",
        "DISCAPACIDAD": "against_disabled",
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
    against_religion = models.BooleanField(default=False)
    against_disabled = models.BooleanField(default=False)
