from django.db import models
from .comment import Comment
from .article_label import ArticleLabel


class CommentLabel(models.Model):
    """
    Comment Label class:

    This represents a labelling from a user of a specific
    """
    HATE_SPEECH_TYPES = [
        ('', 'Ninguno'),
        ('MUJER', 'Violencia contra las mujeres'),
        ('GENERO', 'Identidad de género u orientación sexual'),
        ('RACISMO', 'Racismo o xenofobia'),
        ('POBREZA', 'Pobreza, situación socioeconómica, barrio de residencia'),
        ('RELIGION', 'Religión'),
        ('DISCAPACIDAD', 'Discapacidad o Salud Mental'),
    ]

    is_hateful = models.BooleanField(blank=False, null=False)
    calls_for_action = models.BooleanField(blank=False, null=False)

    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="labels"
    )
    article_label = models.ForeignKey(
        ArticleLabel, on_delete=models.CASCADE, related_name="comment_labels"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=15, choices=HATE_SPEECH_TYPES)
