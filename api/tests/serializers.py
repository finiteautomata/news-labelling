from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Assignment
from .factories import ArticleFactory
from ..serializers import ArticleLabelSerializer

class ArticleLabelSerializerTest(TestCase):
    """
    Tests for validation and save of ArticleLabelSerializer
    """
    def setUp(self):
        self.article = ArticleFactory(create_comments__num_comments=10)
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )


    def create_serializer(self, data, assignment=False, article=None):
        """
        Create serializer with data and context
        """

        if not article:
            article = self.article

        if assignment:
            self.create_assignment(article)

        return ArticleLabelSerializer(
            data=data, context={'article': article, 'user': self.user}
        )

    def create_assignment(self, article):
        """
        Creates assignment for user and article
        """
        return self.user.assignment_set.create(article=article)

    def test_is_not_valid_if_no_assignment(self):
        """
        If no assignment, then it is not valid
        """

        serializer = self.create_serializer({
            "is_interesting": False,
        })

        assert not serializer.is_valid()


    def test_is_valid_if_not_interesting(self):
        """
        If is not interesting, it should be valid
        """
        serializer = self.create_serializer({
            "is_interesting": False,
        }, assignment=True)



        assert serializer.is_valid()

    def test_not_valid_if_already_labeled(self):
        """
        If is not interesting, it should be valid
        """
        serializer = self.create_serializer({
            "is_interesting": False,
        }, assignment=True)

        another_serializer = self.create_serializer({
            "is_interesting": False,
        })

        serializer.is_valid()
        serializer.save()

        assert not another_serializer.is_valid()



    def test_not_valid_if_not_interesting_and_has_labels(self):
        """
        Not valid if has labels and not interesting
        """
        serializer = self.create_serializer({
            "is_interesting": False,
            "comment_labels": [
                {"is_hateful": True, "comment": 1}
            ],
        }, assignment=True)

        assert not serializer.is_valid()

    def test_valid_if_interesting_and_has_labels_for_every_comment(self):
        """
        Valid if interesting and labels for every comment
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                {"is_hateful": True, "comment": comm.id, "type": "RACISMO"}
                for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert serializer.is_valid()

    def test_not_valid_if_lacks_type(self):
        """
        Valid if interesting and labels for every comment
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                {"is_hateful": True, "comment": comm.id}
                for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert not serializer.is_valid()

    def test_not_valid_if_type_empty_when_hateful(self):
        """
        Not valid if hateful but type is empty
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                {"is_hateful": True, "comment": comm.id, "type": ''}
                for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert not serializer.is_valid()

    def test_not_valid_if_type_non_empty_when_not_hateful(self):
        """
        Not Valid if not hateful but non empty type
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                {"is_hateful": False, "comment": comm.id, "type": 'RACISMO'}
                for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert not serializer.is_valid()

    def test_valid_with_two_different_comments(self):
        """
        Test for two comments
        """
        article = ArticleFactory(create_comments__num_comments=2)
        comments = list(article.comment_set.all())

        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                {"is_hateful": False, "comment": comments[0].id, "type": ''},
                {"is_hateful": True, "comment": comments[1].id, "type": 'RACISMO'}
            ],
        }, assignment=True, article=article)
        assert serializer.is_valid()

    def test_not_valid_if_interesting_but_lacks_label_for_comment(self):
        """
        Not valid if lacks a label
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                {"is_hateful": True, "comment": comm.id}
                for comm in self.article.comment_set.all()[:3]
            ],
        }, assignment=True)

        assert not serializer.is_valid()

    def test_create_for_not_interesting(self):
        """
        Test creation for not interesting article
        """
        serializer = self.create_serializer({
            "is_interesting": False,
        }, assignment=True)

        assert serializer.is_valid()
        article_label = serializer.save()

        assert article_label.comment_labels.count() == 0

    def test_create_for_interesting(self):
        """
        Test creation for interesting article
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                {"is_hateful": True, "comment": comm.id, "type": "MUJER"}
                for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert serializer.is_valid()
        article_label = serializer.save()

        self.assertEqual(
            article_label.comment_labels.count(),
            self.article.comment_set.count()
        )

    def test_assignment_is_done_after_creating(self):
        """
        Test creation for interesting article
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                {"is_hateful": True, "comment": comm.id, "type": "RELIGION"}
                for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert serializer.is_valid()
        serializer.save()

        assignment = self.article.assignment_set.get(user=self.user)

        assert assignment.done
