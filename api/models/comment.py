from django.db import models
from .article import Article

class Comment(models.Model):
    """
    Comment class
    """
    text = models.CharField(max_length=350, blank=False)
    user_id = models.PositiveBigIntegerField()
    tweet_id = models.PositiveBigIntegerField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
