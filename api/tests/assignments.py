from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User
from .factories import ArticleFactory, ArticleLabelFactory, UserFactory, ArticleLabel
from ..models import Assignment


class AssignmentTest(TestCase):
    """
    Tests for validation and save of ArticleLabelSerializer
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )


    def test_next_is_first_assignment(self):
        """
        Get first assignment
        """
        article = ArticleFactory()
        Assignment.objects.create(user=self.user, article=article)

        next_assignment = Assignment.next_assignment_of(self.user)
        self.assertEqual(next_assignment.article, article)

    def test_next_is_the_first_not_done(self):
        """
        Test we get the first not-done assignment
        """
        articles = ArticleFactory.create_batch(5)
        assignments = [
            Assignment.objects.create(user=self.user, article=article)
            for article in articles
        ]

        assignments[0].complete()
        assignments[1].complete()

        next_assignment = Assignment.next_assignment_of(self.user)

        self.assertEqual(next_assignment.article, articles[2])

    def test_raise_if_no_next_assignment(self):
        """
        Test it raises if no next assignment
        """
        articles = ArticleFactory.create_batch(5)


        for article in articles:
            Assignment.objects.create(user=self.user, article=article, done=True)

        assignment = Assignment.next_assignment_of(self.user)

        self.assertEqual(assignment, None)


    def test_raise_if_call_complete_twice(self):
        """
        Test it raises if no next assignment
        """
        article = ArticleFactory()
        assignment = Assignment.objects.create(user=self.user, article=article)

        assignment.complete()

        with self.assertRaises(ValueError):
            assignment.complete()


    def test_two_assignments_to_same_article_and_user_are_invalid(self):
        """
        Test it raises if no next assignment
        """
        article = ArticleFactory()
        Assignment.objects.create(user=self.user, article=article)

        with self.assertRaises(IntegrityError):
            Assignment.objects.create(user=self.user, article=article)

    def test_assignment_completed_after_article_label_created(self):
        """
        Assignment must be completed on creation of ArticleLabel
        """

        article = ArticleFactory()
        assignment = Assignment.objects.create(user=self.user, article=article)

        # Stimulus

        ArticleLabelFactory(article=article, user=self.user)

        assignment.refresh_from_db()

        self.assertIs(assignment.done, True)

    def test_assignment_returns_to_undone_if_label_deleted(self):
        """
        Assignment must be completed on creation of ArticleLabel
        """

        article = ArticleFactory()
        assignment = Assignment.objects.create(user=self.user, article=article)

        # Stimulus
        article_label = ArticleLabelFactory(article=article, user=self.user)
        article_label.delete()

        assignment.refresh_from_db()

        self.assertIs(assignment.done, False)


