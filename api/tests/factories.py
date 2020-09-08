import factory
from django.utils import timezone
from ..models import Article, Comment



class ArticleFactory(factory.django.DjangoModelFactory):
    """
    Article Factory
    """
    class Meta:
        """
        Meta class
        """
        model = Article

    title = factory.Sequence(lambda n: f"Artículo num {n}")
    tweet_id = factory.Sequence(lambda n: 1000 + n)
    text = "Este es el tweet"
    slug = factory.Sequence(lambda n: f"slug-{n}")
    url = "http://clarin.com"
    user = "clarincom"
    body = "Lorem ipsum pepe"
    created_at = timezone.now()

    @factory.post_generation
    def create_comments(self, create, extracted, num_comments=2, **kwargs):
        """
        Create comments after initialization
        """
        for i in range(num_comments):
            CommentFactory.create(article=self)

class CommentFactory(factory.django.DjangoModelFactory):
    """
    Comment Factory
    """
    class Meta:
        """
        Meta class
        """
        model = Comment

    text = factory.Sequence(lambda n: f"Comentario num {n}")
    user_id = 110001110001
    tweet_id = factory.Sequence(lambda n: 2000 + n)
    article = factory.SubFactory(ArticleFactory)
    created_at = timezone.now()
