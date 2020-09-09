from django.db import models
from .comment import Comment
from .article_label import ArticleLabel

class CommentLabel(models.Model):
    """
    Comment Label class:

    This represents a labelling from a user of a specific
    """
    is_hateful = models.BooleanField(blank=False, null=False)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="labels"
    )
    article_label = models.ForeignKey(
        ArticleLabel, on_delete=models.CASCADE, related_name="comment_labels"
    )
    created_at = models.DateTimeField(auto_now_add=True)
