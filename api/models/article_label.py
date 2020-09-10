from django.contrib.auth.models import User
from django.db import models
from .article import Article

class ArticleLabel(models.Model):
    """
    Article Label class:

    This represents a labelling from a user of a specific article

    Each Article label might have or not have a number of Comment labels
    (depending on whether they are interesting or not)
    """
    is_interesting = models.BooleanField(blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="labels"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
