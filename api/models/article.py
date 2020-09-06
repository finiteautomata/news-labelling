from django.db import models

# Create your models here.
class Article(models.Model):
    """
    Article class
    """
    title = models.CharField(max_length=300, blank=False)
    tweet_id = models.PositiveBigIntegerField()
    text = models.CharField(blank=False, max_length=500)
    slug = models.CharField(blank=False, max_length=130, unique=True)
    title = models.CharField(blank=False, max_length=200)
    url = models.CharField(blank=False, max_length=200)

    user = models.CharField(max_length=40)
    body = models.TextField()
    created_at = models.DateTimeField()
