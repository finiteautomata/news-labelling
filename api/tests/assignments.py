from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .factories import ArticleFactory, ArticleLabelFactory, UserFactory, ArticleLabel, BatchFactory
from ..models import Assignment, AssignmentComment, Assigner
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

class AssignerTest(TestCase):

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

        self.articles = batch.articles.all()

    def test_assigns_to_user_creates_assignment(self):
        """
        Assign article to user
        """
        an_article = self.articles[0]

        assigner = Assigner()
        assignment = assigner.assign(an_article, self.user)

        self.assertIsNotNone(assignment)
        self.assertIs(assignment.user, self.user)
        self.assertIs(assignment.article, an_article)

    def test_assigns_twice_to_user_does_nothing(self):
        """
        Assign article to user
        """

        an_article = self.articles[0]

        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.user)

        self.assertIs(self.user.assignment_set.count(), 1)


    def test_assigning_to_another_user_just_assigns_it(self):
        """
        No problem if assign article to one and then to another
        """
        an_article = self.articles[0]

        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assignment = assigner.assign(an_article, self.another_user)

        self.assertIs(assignment.user, self.another_user)

    def test_assigning_to_another_user_assigns_all_comments(self):
        """
        No problem if assign article to one and then to another
        """
        an_article = self.articles[0]

        assigner = Assigner()
        assigner.assign(an_article, self.user)

        assignment = assigner.assign(an_article, self.another_user)
        self.assertIs(assignment.user, self.another_user)

        self.assertCountEqual(
            assignment.comments_to_label(),
            an_article.comment_set.all()
        )
        ## Label

        #label_article(self.another_user, self.article, is_interesting=False)
        #self.skipped_assignment = self.article.assignment_set.get(user=self.another_user)

    def set_skipped_and_labeled_article(self, hateful_labels=[True, False, False]):
        """
        Custom setup
        """
        an_article = self.articles[0]

        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.another_user)

        annotated_assignment = label_article(
            self.user, an_article, is_interesting=True, comments=[
            {"is_hateful": hateful_labels[0]},
            {"is_hateful": hateful_labels[1]},
            {"is_hateful": hateful_labels[2]},
        ])

        return label_article(
            self.another_user, an_article, is_interesting=False
        )


    def test_reassign_for_two_users_if_one_skipped_reassigns_only_hateful_comments(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """

        skipped_assignment = self.set_skipped_and_labeled_article()

        assigner = Assigner()
        assigner.assign(skipped_assignment.article, skipped_assignment.user, reassign=True)

        skipped_assignment.refresh_from_db()
        self.assertIs(skipped_assignment.done, False)

    def test_reassign_for_three_users_if_one_skipped_reassigns_only_hateful_comments(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """
        yet_another_user = User.objects.create_user(
            username="yet_another_user",
            password="test",
        )
        an_article = self.articles[0]

        comments = list(an_article.comment_set.all())
        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.another_user)

        # Note. I create this by hand because my rule for three annotators was different
        an_article.assignment_set.create(user=yet_another_user)

        label_article(
            self.user, an_article, is_interesting=True, comments=[
            {"is_hateful": True},
            {"is_hateful": False},
            {"is_hateful": False},
        ])

        label_article(
            self.another_user, an_article, is_interesting=True, comments=[
            {"is_hateful": False},
            {"is_hateful": True},
            {"is_hateful": False},
        ])

        label_article(
            yet_another_user, an_article, is_interesting=False
        )

        assignment = assigner.assign(an_article, yet_another_user, reassign=True)

        self.assertIs(assignment.done, False)
        self.assertEqual(assignment.user, yet_another_user)
        self.assertEqual(assignment.skippable, False)
        self.assertSequenceEqual(
            assignment.comments_to_label(),
            comments[:2],
        )

    def test_reassign_if_everyone_skipped_raises(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """
        yet_another_user = User.objects.create_user(
            username="yet_another_user",
            password="test",
        )
        an_article = self.articles[0]

        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.another_user)

        # Note. I create this by hand because my rule for three annotators was different
        an_article.assignment_set.create(user=yet_another_user)

        label_article(
            self.user, an_article, is_interesting=False
        )

        label_article(
            self.another_user, an_article, is_interesting=False
        )

        label_article(
            yet_another_user, an_article, is_interesting=False
        )

        with self.assertRaises(ValueError):
            assigner.assign(an_article, yet_another_user, reassign=True)


    def test_reassign_undo_assignment_with_hateful_set_it_as_not_skippable(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """
        skipped_assignment = self.set_skipped_and_labeled_article()

        assigner = Assigner()
        assigner.assign(skipped_assignment.article, skipped_assignment.user, reassign=True)

        skipped_assignment.refresh_from_db()
        self.assertIs(skipped_assignment.skippable, False)

    def test_reassign_sets_only_comments_that_were_marked_as_hateful(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """

        skipped_assignment = self.set_skipped_and_labeled_article()

        assigner = Assigner()
        assigner.assign(skipped_assignment.article, skipped_assignment.user, reassign=True)
        skipped_assignment.refresh_from_db()

        annotated_label = skipped_assignment.article.labels.get(
            is_interesting=True,
            user=self.user
        )
        possibly_hateful_comments = [
            comment_label.comment
            for comment_label in annotated_label.comment_labels.all() if comment_label.is_hateful
        ]

        self.assertSequenceEqual(
            skipped_assignment.comments.all(),
            possibly_hateful_comments
        )

    def test_reassign_for_second_annotation_on_no_hateful_does_not_reset(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """

        skipped_assignment = self.set_skipped_and_labeled_article(
            hateful_labels=[False, False, False]
        )

        assigner = Assigner()
        assigner.assign(skipped_assignment.article, skipped_assignment.user, reassign=True)


        self.assertIs(
            skipped_assignment.done,
            True
        )

    def test_reassign_wrt_skipped_assignment_raises(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """

        an_article = self.articles[0]

        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.another_user)

        label_article(
            self.user, an_article, is_interesting=False
        )

        label_article(
            self.another_user, an_article, is_interesting=False
        )

        with self.assertRaises(ValueError):
            assigner.assign(an_article, self.another_user, reassign=True)

    def test_reassign_wrt_not_done_assignment_raises(self):
        """
        Test article is reassigned for those articles which one of them skipped and not the other
        """

        an_article = self.articles[0]

        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.another_user)

        label_article(
            self.user, an_article, is_interesting=False
        )

        with self.assertRaises(ValueError):
            assigner.assign(an_article, self.another_user, reassign=True)

    def test_assign_for_third_only_hateful_comments(self):
        """
        Test article is assigned for third only assigns hateful comments
        """
        yet_another_user = User.objects.create_user(
            username="yet_another_user",
            password="test",
        )
        an_article = self.articles[0]

        comments = list(an_article.comment_set.all())
        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.another_user)

        label_article(
            self.user, an_article, is_interesting=True, comments=[
            {"is_hateful": True},
            {"is_hateful": False},
            {"is_hateful": False},
        ])

        label_article(
            self.another_user, an_article, is_interesting=True, comments=[
            {"is_hateful": False},
            {"is_hateful": True},
            {"is_hateful": False},
        ])

        assignment = assigner.assign(an_article, yet_another_user, reassign=True)

        self.assertIs(assignment.done, False)
        self.assertEqual(assignment.user, yet_another_user)
        self.assertEqual(assignment.skippable, False)
        self.assertSequenceEqual(
            assignment.comments_to_label(),
            comments[:2],
        )

    def test_assign_for_third_assigns_comments_with_one_or_two_votes(self):
        """
        Test article is assigned for third only assigns hateful comments
        """
        yet_another_user = User.objects.create_user(
            username="yet_another_user",
            password="test",
        )
        an_article = self.articles[0]

        comments = list(an_article.comment_set.all())
        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.another_user)

        label_article(
            self.user, an_article, is_interesting=True, comments=[
            {"is_hateful": True},
            {"is_hateful": False},
            {"is_hateful": False},
        ])

        label_article(
            self.another_user, an_article, is_interesting=True, comments=[
            {"is_hateful": True},
            {"is_hateful": False},
            {"is_hateful": True},
        ])

        assignment = assigner.assign(an_article, yet_another_user, reassign=True)

        self.assertIs(assignment.done, False)
        self.assertEqual(assignment.user, yet_another_user)
        self.assertEqual(assignment.skippable, False)
        self.assertSequenceEqual(
            assignment.comments_to_label(),
            [comments[0], comments[2]],
        )


    def test_assign_for_third_if_no_hateful_does_not_assign(self):
        """
        Test article is assigned for third without hateful
        """
        yet_another_user = User.objects.create_user(
            username="yet_another_user",
            password="test",
        )
        an_article = self.articles[0]

        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.another_user)

        label_article(
            self.user, an_article, is_interesting=True, comments=[
            {"is_hateful": False},
            {"is_hateful": False},
            {"is_hateful": False},
        ])

        label_article(
            self.another_user, an_article, is_interesting=True, comments=[
            {"is_hateful": False},
            {"is_hateful": False},
            {"is_hateful": False},
        ])

        assignment = assigner.assign(an_article, yet_another_user, reassign=True)

        self.assertIs(assignment, None)
        self.assertEqual(yet_another_user.assignment_set.count(), 0)

    def test_assign_for_third_if_no_hateful_and_skipped_does_not_assign(self):
        """
        Test article is assigned for third without hateful
        """
        yet_another_user = User.objects.create_user(
            username="yet_another_user",
            password="test",
        )
        an_article = self.articles[0]

        assigner = Assigner()
        assigner.assign(an_article, self.user)
        assigner.assign(an_article, self.another_user)

        label_article(
            self.user, an_article, is_interesting=False
        )

        label_article(
            self.another_user, an_article, is_interesting=True, comments=[
            {"is_hateful": False},
            {"is_hateful": False},
            {"is_hateful": False},
        ])

        assignment = assigner.assign(an_article, yet_another_user, reassign=True)

        self.assertIs(assignment, None)
        self.assertEqual(yet_another_user.assignment_set.count(), 0)