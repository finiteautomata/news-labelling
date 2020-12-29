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
        """
        Test cannot create with same name
        """
        Batch.objects.create(name="name")

        with self.assertRaises(IntegrityError):
            Batch.objects.create(name="name")

    def test_create_with_articles(self):
        """
        Test convenience method
        """
        articles = ArticleFactory.create_batch(5)
        batch = Batch.create_from_articles(name="name", articles=articles)

        assert batch.pk is not None
        self.assertIs(batch.articles.count(), len(articles))

    def test_assign_to_user_creates_assignments(self):
        """
        Test assign_to creates assignments
        """
        articles = ArticleFactory.create_batch(5)
        batch = Batch.create_from_articles(name="batch name", articles=articles)

        batch.assign_to(self.user)

        self.assertListEqual(
            [assign.article.id for assign in self.user.assignment_set.all()],
            [art.id for art in articles]
        )

    def test_is_assigned_after_assign_to(self):
        """
        Test is_assigned returns True after assign_to
        """
        articles = ArticleFactory.create_batch(5)
        batch = Batch.create_from_articles(name="batch name", articles=articles)

        batch.assign_to(self.user)

        self.assertIs(batch.is_assigned_to(self.user), True)

    def test_assigning_twice_raises(self):
        """
        Check cannot assign twice
        """
        articles = ArticleFactory.create_batch(5)
        batch = Batch.create_from_articles(name="batch name", articles=articles)

        batch.assign_to(self.user)

        with self.assertRaises(IntegrityError):
            batch.assign_to(self.user)