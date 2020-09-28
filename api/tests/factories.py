import factory
from django.utils import timezone
from ..models import Article, Comment


def comment_label(
    comment_id, is_hateful=True, calls_for_action=False, types=None):
    """
    'Factory' for comment_label
    """

    if not is_hateful:
        calls_for_action = False
        types = []
    else:
        types = types or ["RACISMO"]

    return {
        "comment": comment_id,
        "is_hateful": is_hateful,
        "types": types,
        "calls_for_action": calls_for_action
    }



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
    def create_comments(self, *args, **kwargs):
        """
        Create comments after initialization

        If you want to change number of comments created, use something like this:

        >> ArticleFactory(create_comments__num_comments=10)
        """
        num_comments = kwargs.get("num_comments", 3)
        CommentFactory.create_batch(num_comments, article=self)

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
