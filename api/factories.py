import datetime
import factory
from .models import Article


class ArticleFactory(factory.django.DjangoModelFactory):
    """
    Article Factory
    """
    class Meta:
        """
        Meta class
        """
        model = Article

    title = "Título de artículo"
    tweet_id = factory.Sequence(lambda n: 1000 + n)
    text = "Este es el tweet"
    slug = factory.Sequence(lambda n: f"slug-{n}")
    url = "http://clarin.com"
    user = "clarincom"
    body = "Lorem ipsum pepe"
    created_at = datetime.datetime.now()
