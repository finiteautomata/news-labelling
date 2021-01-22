from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User
from .factories import ArticleFactory, ArticleLabelFactory, UserFactory, ArticleLabel
from ..models import Batch


class BatchTest(TestCase):
    """
    Tests for validation and save of Batch
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

    def test_assigning_twice_creates_no_new_assignments(self):
        """
        Check cannot assign twice
        """
        articles = ArticleFactory.create_batch(5)
        batch = Batch.create_from_articles(name="batch name", articles=articles)

        batch.assign_to(self.user)

        assignments_count = self.user.assignment_set.count()

        batch.assign_to(self.user)

        self.assertIs(assignments_count, self.user.assignment_set.count())

    def test_revokes_from_user_when_not_started(self):
        """
        Check it can be revoked when not started
        """
        articles = ArticleFactory.create_batch(5)
        batch = Batch.create_from_articles(name="batch name", articles=articles)

        batch.assign_to(self.user)
        batch.revoke_from(self.user)

        self.assertIs(batch.is_assigned_to(self.user), False)

    def test_revokes_only_deletes_current_assignments(self):
        """
        Check it can be revoked when not started
        """
        articles1 = ArticleFactory.create_batch(5)
        articles2 = ArticleFactory.create_batch(5)

        batch1 = Batch.create_from_articles(name="1", articles=articles1)
        batch1.assign_to(self.user)

        batch2 = Batch.create_from_articles(name="2", articles=articles2)
        batch2.assign_to(self.user)


        batch1.revoke_from(self.user)

        self.assertIs(batch2.is_assigned_to(self.user), True)
        self.assertIs(
            self.user.assignment_set.filter(article__in=articles2).count(),
            len(articles2),
        )
        self.assertIs(self.user.assignment_set.count(), len(articles2))

    def test_raises_when_already_set(self):
        """
        Check it can be revoked when not started
        """
        articles = ArticleFactory.create_batch(5)

        batch = Batch.create_from_articles(name="1", articles=articles)
        batch.assign_to(self.user)

        self.user.article_labels.create(article=articles[0], is_interesting=False)
        with self.assertRaises(ValueError):
            batch.revoke_from(self.user)


class BatchAssignmentTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )
        self.articles = ArticleFactory.create_batch(5)
        self.batch = Batch.create_from_articles(name="batch name", articles=self.articles)



    def test_batch_assignment_not_done_after_creation(self):
        """
        Check assignment not done after creation
        """

        batch_assignment = self.batch.assign_to(self.user)

        self.assertIs(batch_assignment.done, False)

    def test_batch_assignment_not_done_after_just_one_label(self):
        """
        Check assignment not done after creation
        """
        batch_assignment = self.batch.assign_to(self.user)
        ArticleLabelFactory(article=self.articles[0], user=self.user)

        self.assertIs(batch_assignment.done, False)

    def test_batch_assignment_done_after_just_all_labels(self):
        """
        Check assignment not done after creation
        """
        batch_assignment = self.batch.assign_to(self.user)

        for art in self.articles:
            ArticleLabelFactory(article=art, user=self.user)


        self.assertIs(batch_assignment.done, True)

    def test_completed_articles_when_just_started(self):
        """
        Check assignment not done after creation
        """
        batch_assignment = self.batch.assign_to(self.user)

        self.assertIs(batch_assignment.completed_articles, 0)

    def test_completed_articles_after_few_labels(self):
        """
        Check assignment not done after creation
        """
        batch_assignment = self.batch.assign_to(self.user)

        for art in self.articles[:3]:
            ArticleLabelFactory(article=art, user=self.user)

        self.assertIs(batch_assignment.completed_articles, 3)



    def test_update_after_removing(self):
        """
        Check assignment not done after creation
        """
        batch_assignment = self.batch.assign_to(self.user)

        for art in self.articles:
            ArticleLabelFactory(article=art, user=self.user)

        self.assertIs(batch_assignment.done, True)
        # Let's remove the article label from last article

        ArticleLabel.objects.filter(article=self.articles[-1]).delete()

        self.assertIs(batch_assignment.done, False)