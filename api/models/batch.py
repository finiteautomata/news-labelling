from django.db import models
from api.models import Article

# Create your models here.
class Batch(models.Model):
    """
    Batch model
    """
    name = models.CharField(max_length=300, blank=False, unique=True)
    articles = models.ManyToManyField(Article, through="BatchArticle")


class BatchArticle(models.Model):
    """
    Batch relationship model
    """

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

