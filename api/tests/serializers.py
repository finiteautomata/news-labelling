from django.test import TestCase
from .factories import ArticleFactory
from ..serializers import ArticleLabelSerializer

class ArticleLabelSerializerTest(TestCase):
    """
    Tests for validation and save of ArticleLabelSerializer
    """
    def setUp(self):
        self.article = ArticleFactory(create_comments__num_comments=10)

    def create_serializer(self, data):
        """
        Create serializer with data and context
        """
        return ArticleLabelSerializer(
            data=data, context={'article': self.article}
        )

    def test_is_valid_if_not_interesting(self):
        """
        If is not interesting, it should be valid
        """
        serializer = self.create_serializer({
            "is_interesting": False,
        })

        assert serializer.is_valid()

    def test_not_valid_if_not_interesting_and_has_labels(self):
        """
        Not valid if has labels and not interesting
        """
        serializer = self.create_serializer({
            "is_interesting": False,
            "comment_labels": [
                {"is_hateful": True, "comment": 1}
            ],
        })

        assert not serializer.is_valid()

    def test_valid_if_interesting_and_has_labels_for_every_comment(self):
        """
        Valid if interesting and labels for every comment
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                {"is_hateful": True, "comment": comm.id}
                for comm in self.article.comment_set.all()
            ],
        })

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
        })

        assert not serializer.is_valid()
