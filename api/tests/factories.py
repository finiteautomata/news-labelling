import factory
from django.utils import timezone
from django.contrib.auth.models import User
from ..models import Article, Batch, Comment, ArticleLabel, CommentLabel

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Sequence(lambda n: "Agent %03d" % n)
    username = factory.Faker('user_name')

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



class BatchFactory(factory.django.DjangoModelFactory):
    """
    Article Factory
    """
    class Meta:
        """
        Meta class
        """
        model = Batch

    name = factory.Sequence(lambda n: f"{n}")

    @factory.post_generation
    def create_articles(self, *args, **kwargs):
        """
        Create comments after initialization

        If you want to change number of comments created, use something like this:

        >> BatchFactory(create_articles__num_articles=10)
        """
        num_articles = kwargs.get("num", 3)
        num_comments = kwargs.get("num_comments", 3)
        ArticleFactory.create_batch(
            num_articles, batch=self,
            create_comments__num_comments=num_comments
        )

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

class CommentLabelFactory(factory.django.DjangoModelFactory):
    """
    Comment Label Factory
    """

    is_hateful = True
    calls_for_action = False

    class Meta:
        """
        Meta class
        """
        model = CommentLabel

    comment = factory.SubFactory(CommentFactory)
    against_women = True
    against_lgbti = False
    against_race = False
    against_poor = False
    against_political = False
    against_disabled = False
    against_aspect = False
    against_criminals = False
    against_others = False

class ArticleLabelFactory(factory.django.DjangoModelFactory):
    """
    Article Label Factory
    """
    class Meta:
        """
        Meta class
        """
        model = ArticleLabel
    is_interesting = True
    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def create_comment_labels(self, *args, **kwargs):
        """
        Create comments labels after initialization
        """
        article = self.article
        for comment in article.comment_set.all():
            CommentLabelFactory(comment=comment, article_label=self)
