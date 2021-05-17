from django.test import TestCase
from .comment_serializer import CommentSerializer
from . import field_mapping, field_translation
from api.models import CommentLabel
from api.tests.factories import UserFactory, ArticleFactory, CommentLabelFactory


def label_article(user, article, is_interesting, comments=None):
    """
    Label article
    """
    if not user.assignment_set.filter(article=article).exists():
        user.assignment_set.create(article=article)
    user.article_labels.create(article=article, is_interesting=is_interesting)

    if is_interesting:
        if not comments or len(comments) != article.comment_set.count():
            raise ValueError("comments argument must be same size of comments")

        for label_args, comment in zip(comments, article.comment_set.all()):
            CommentLabelFactory.create_from_labels(
                comment=comment, user=user,
                labels=label_args
            )

    return article.assignment_set.get(user=user)

keys = ["HATEFUL", "CALLS"] + list(CommentLabel.type_mapping)
keys.remove("OTROS")

def assert_comment_label(serialized_label, labels):
    for key in keys:
        translation = field_translation[key]
        if key in labels:
            actual = len(serialized_label[translation])
            error_msg = f"{key} --> {actual} votes, {labels[key]} expected"
            assert  actual == labels[key], error_msg
        else:
            assert len(serialized_label[translation]) == 0


class CommentSerializerTest(TestCase):
    """
    Tests for validation and save of ArticleLabelSerializer
    """
    def setUp(self):
        """
        Setup
        """
        self.article = ArticleFactory(create_comments__num_comments=3)
        self.comments = self.article.comment_set.all()
        self.annotators = sorted(
            UserFactory.create_batch(3),
            key=lambda x: x.username
        )

    def test_anonymized_names(self):
        """
        Get first assignment
        """
        for annotator in self.annotators:
            label_article(annotator, self.article, is_interesting=False)

        serializer = CommentSerializer(annotators=self.annotators)

        for i, annotator in enumerate(self.annotators):
            self.assertEqual(
                f"annotator_{i+1}",
                serializer.anonymized_names[annotator.username]
            )

    def test_non_hateful_comment(self):
        """
        Get first assignment
        """
        annotators = sorted(
            UserFactory.create_batch(5),
            key=lambda x: x.username
        )

        for annotator in annotators:
            label_article(annotator, self.article, is_interesting=True, comments=[
                [],
                [],
                [],
            ])

        serializer = CommentSerializer(raw=True)

        for comment in self.article.comment_set.all():
            serialized_comment = serializer.serialize(comment)

            for key in field_mapping:
                self.assertCountEqual(
                    serialized_comment[key],
                    []
                )

    def setUpHatefulComment(self):
        """
        Custom setup
        """
        self.annotators = sorted(
            UserFactory.create_batch(5),
            key=lambda x: x.username
        )

        label_article(self.annotators[0], self.article, is_interesting=True, comments=[
            ["HATE", "MUJER"],
            [],
            [],
        ])

        label_article(self.annotators[1], self.article, is_interesting=True, comments=[
            ["HATE", "MUJER", "ASPECTO"],
            [],
            [],
        ])

        label_article(self.annotators[3], self.article, is_interesting=True, comments=[
            [],
            [],
            ["HATE", "OTROS"],
        ])


    def test_hateful_comment_votes(self):
        """
        """

        self.setUpHatefulComment()

        serializer = CommentSerializer(raw=True)
        serialized_comment = serializer.serialize(self.comments[0])

        assert_comment_label(serialized_comment, {
            "HATEFUL": 2,
            "MUJER": 2,
            "ASPECTO": 1,
        })

    def test_annotators(self):
        """
        """
        self.setUpHatefulComment()

        serializer = CommentSerializer(annotators=self.annotators)
        serialized_comment = serializer.serialize(self.comments[0])

        self.assertCountEqual(
            serialized_comment["annotators"],
            ["annotator_1", "annotator_2", "annotator_4"],
        )

    def test_tweet_id_not_included(self):
        """
        Get first assignment
        """
        self.setUpHatefulComment()

        serializer = CommentSerializer(annotators=self.annotators)
        serialized_comment = serializer.serialize(self.comments[0])

        assert "tweet_id" not in serialized_comment["annotators"]

    def test_tweet_id_included_if_not_anonymize(self):
        """
        """
        self.setUpHatefulComment()

        comment = self.comments[0]

        serializer = CommentSerializer(anonymize=False)
        serialized_comment = serializer.serialize(comment)

        self.assertEqual(serialized_comment["tweet_id"], str(comment.tweet_id))


    def test_ignore_labelled_as_others(self):
        """
        """
        self.setUpHatefulComment()

        comment = self.comments[2]

        serializer = CommentSerializer(anonymize=False, raw=True)
        serialized_comment = serializer.serialize(comment)

        assert_comment_label(serialized_comment, {
            "HATEFUL": 0,
        })