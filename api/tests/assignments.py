from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .factories import ArticleFactory, ArticleLabelFactory, UserFactory, ArticleLabel, BatchFactory
from ..models import Assignment, AssignmentComment
from .helpers import label_article


class AssignmentTest(TestCase):
    """
    Tests for validation and save of ArticleLabelSerializer
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )

        self.another_user = User.objects.create_user(
            username="another_test",
            password="another_test",
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

    def test_create_assignment_with_two_comments(self):
        """
        Can create assignment with two comments
        """

        article = ArticleFactory()

        assignment = Assignment.objects.create(user=self.user, article=article)

        assignment.set_comments(article.comment_set.all()[:2])

    def test_cannot_assign_comments_from_other_article(self):
        """
        Cannot set comments from other article
        """

        article1 = ArticleFactory()
        article2 = ArticleFactory()

        assignment = Assignment.objects.create(user=self.user, article=article1)

        with self.assertRaises(ValidationError):
            assignment.set_comments(article2.comment_set.all()[:2])

        assignment.refresh_from_db()

        self.assertIs(assignment.comments.count(), 0)


    def test_comments_to_label_without_setting_are_all_comments(self):
        """
        Cannot set comments from other article
        """

        article = ArticleFactory()

        assignment = Assignment.objects.create(user=self.user, article=article)

        self.assertSetEqual(
            article.comment_set.all(),
            assignment.comments_to_label(),
        )

    def test_comments_to_label_returns_set_comments(self):
        """
        Cannot set comments from other article
        """

        article = ArticleFactory()

        assignment = Assignment.objects.create(user=self.user, article=article)

        articles_to_label = list(article.comment_set.all()[:2])
        assignment.set_comments(articles_to_label)

        assert 2 == assignment.comments.count()
        assert assignment.comments.count() < article.comment_set.all().count()

        self.assertSequenceEqual(
            assignment.comments_to_label(),
            articles_to_label,
        )

class AssignmentReassign(TestCase):

    """
    Tests for Assignment reassing_for
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )

        self.another_user = User.objects.create_user(
            username="another_test",
            password="another_test",
        )

        batch = BatchFactory(create_articles__num=2, create_articles__num_comments=3)

        articles = batch.articles.all()

        batch.assign_to(self.user)
        batch.assign_to(self.another_user)

        self.article = articles[0]

        ## Label

        label_article(self.another_user, self.article, is_interesting=False)
        self.skipped_assignment = self.article.assignment_set.get(user=self.another_user)

    def test_reassign_undo_assignment(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """
        annotated_assignment = label_article(
            self.user, self.article, is_interesting=True, comments=[
            {"is_hateful": True},
            {"is_hateful": False},
            {"is_hateful": False},
        ])

        self.skipped_assignment.reassign_for(annotated_assignment)
        self.skipped_assignment.refresh_from_db()

        self.assertIs(self.skipped_assignment.done, False)

    def test_reassign_sets_only_comments_that_were_marked_as_hateful(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """

        annotated_assignment = label_article(
            self.user, self.article, is_interesting=True, comments=[
            {"is_hateful": True},
            {"is_hateful": False},
            {"is_hateful": False},
        ])

        self.skipped_assignment.reassign_for(annotated_assignment, only_comments=True)
        self.skipped_assignment.refresh_from_db()

        annotated_label = annotated_assignment.article_label
        possibly_hateful_comments = [
            comment_label.comment
            for comment_label in annotated_label.comment_labels.all() if comment_label.is_hateful
        ]

        self.assertSequenceEqual(
            self.skipped_assignment.comments.all(),
            possibly_hateful_comments
        )

    def test_reassign_for_second_annotation_on_no_hateful_does_not_reset(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """

        annotated_assignment = label_article(
            self.user, self.article, is_interesting=True, comments=[
            {"is_hateful": False},
            {"is_hateful": False},
            {"is_hateful": False},
        ])

        self.skipped_assignment.reassign_for(annotated_assignment, only_comments=True)
        self.skipped_assignment.refresh_from_db()

        self.assertIs(
            self.skipped_assignment.done,
            True
        )

    def test_reassign_wrt_skipped_assignment_raises(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """

        another_skipped_assignment = label_article(
            self.user, self.article, is_interesting=False
        )

        with self.assertRaises(ValueError):
            self.skipped_assignment.reassign_for(another_skipped_assignment, only_comments=True)

    def test_reassign_wrt_not_done_assignment_raises(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """

        not_done_assignment = Assignment.objects.get(
            user=self.user, article=self.article
        )

        assert not_done_assignment.done is False

        with self.assertRaises(ValueError):
            self.skipped_assignment.reassign_for(not_done_assignment, only_comments=True)
