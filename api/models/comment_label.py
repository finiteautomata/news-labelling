from django.db import models
from .comment import Comment

class CommentLabel(models.Model):
    """
    Comment Label class:

    This represents a labelling from a user of a specific
    """
    is_hateful = models.BooleanField(blank=False, null=False)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="labels"
    )
    created_at = models.DateTimeField(auto_now_add=True)
