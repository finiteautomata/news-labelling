from django.db import models
from api.models import Article
from django.contrib.auth.models import User
from .mixins import Completable

# Create your models here.
class Batch(models.Model):
    """
    Batch model
    """
    name = models.CharField(max_length=300, blank=False, unique=True)
    articles = models.ManyToManyField(Article, through="BatchArticle")
    users = models.ManyToManyField(User, through="BatchAssignment")

    @classmethod
    def create_from_articles(cls, name, articles):
        """
        Convenience method for creating batch
        """
        batch = cls(name=name)
        batch.save()

        batch.articles.set(articles)

        return batch

class BatchArticle(models.Model):
    """
    Batch to article relationship model
    """

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class BatchAssignment(models.Model, Completable):
    """
    Batch to user relationship model
    """

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)


