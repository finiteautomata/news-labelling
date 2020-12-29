from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User
from .factories import ArticleFactory, ArticleLabelFactory, UserFactory, ArticleLabel
from ..models import Batch


class BatchTest(TestCase):
    """
    Tests for validation and save of ArticleLabelSerializer
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )


    def test_cannot_create_with_same_name(self):
        Batch.objects.create(name="name")

        with self.assertRaises(IntegrityError):
            Batch.objects.create(name="name")

    def test_create_with_articles(self):
        articles = ArticleFactory.create_batch(5)
        batch = Batch.create_from_articles(name="name", articles=articles)

        assert batch.pk is not None
        self.assertIs(batch.articles.count(), len(articles))