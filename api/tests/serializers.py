import json
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from .factories import ArticleFactory, comment_label
from ..serializers import ArticleLabelSerializer, CommentLabelForCreationSerializer



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


    def create_serializer(self, data, assignment=False, assignment_args={}, article=None):
        """
        Create serializer with data and context
        """
        if not article:
            article = self.article

        if assignment:
            self.create_assignment(article, **assignment_args)

        now = datetime.datetime.now()
        before = now - datetime.timedelta(minutes=5)

        data["metadata"] = data.get("metadata", None) or json.dumps({
            "start_time": str(before),
            "end_time": str(now),
        })

        return ArticleLabelSerializer(
            data=data, context={'article': article, 'user': self.user}
        )

    def create_assignment(self, article, num_comments=None,**kwargs):
        """
        Creates assignment for user and article
        """
        assignment = self.user.assignment_set.create(article=article, **kwargs)

        if num_comments:
            comments_to_label = self.article.comment_set.all()[:num_comments]
            assignment.set_comments(comments_to_label)

        return assignment

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

    def test_is_not_valid_if_not_interesting_but_not_skippable(self):
        """
        If is not interesting, it should be valid
        """
        serializer = self.create_serializer({
            "is_interesting": False,
        }, assignment=True, assignment_args={"skippable": False})

        assert not serializer.is_valid()

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
                comment_label(comm.id) for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert not serializer.is_valid()

    def test_valid_if_interesting_and_has_labels_for_every_comment(self):
        """
        Valid if interesting and labels for every comment
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [{
                    "is_hateful": True,
                    "types": ["MUJER"],
                    "comment": comm.id,
                    "calls_for_action": False
                } for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert serializer.is_valid()

    def test_not_valid_if_lacks_calls_for_action(self):
        """
        Valid if interesting and labels for every comment
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [{
                "is_hateful": True,
                "comment": comm.id,
                "types": ["LGBTI"],
            } for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert not serializer.is_valid()

    def test_not_valid_if_lacks_type(self):
        """
        Valid if interesting and labels for every comment
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [{
                "is_hateful": True,
                "comment": comm.id,
                "calls_for_action": False,
            } for comm in self.article.comment_set.all()
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
                {"is_hateful": True, "comment": comm.id, "types": []}
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
                {"is_hateful": False, "comment": comm.id, "types": ['RACISMO']}
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
                comment_label(comments[0].id, is_hateful=False),
                comment_label(comments[1].id, is_hateful=True, types=["RACISMO"]),
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
                comment_label(comm.id)
                for comm in self.article.comment_set.all()[:3]
            ],
        }, assignment=True)

        assert not serializer.is_valid()

    def test_valid_if_labels_only_selected_comments(self):
        """
        Valid if labels only specified comments in assignment
        """
        num_comments = 3
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                comment_label(comm.id)
                for comm in self.article.comment_set.all()[:num_comments]
            ],
        }, assignment=True, assignment_args={"num_comments": num_comments})

        assert serializer.is_valid()

    def test_not_valid_if_specified_comments_but_labels_less(self):
        """
        Valid if labels only specified comments in assignment
        """
        num_comments = 3
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                comment_label(comm.id)
                for comm in self.article.comment_set.all()[:num_comments-1]
            ],
        }, assignment=True, assignment_args={"num_comments": num_comments})

        assert not serializer.is_valid()

    def test_not_valid_if_specified_comments_but_labels_more(self):
        """
        Valid if labels only specified comments in assignment
        """
        num_comments = 3
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                comment_label(comm.id)
                for comm in self.article.comment_set.all()[:num_comments+1]
            ],
        }, assignment=True, assignment_args={"num_comments": num_comments})

        assert not serializer.is_valid()


    def test_create_for_not_interesting(self):
        """
        Test creation for not interesting article
        """
        serializer = self.create_serializer({
            "is_interesting": False,
            "feedback": "Esto apesta",
        }, assignment=True)

        assert serializer.is_valid()
        article_label = serializer.save()

        self.assertEqual(article_label.feedback, "Esto apesta")
        assert article_label.comment_labels.count() == 0

    def test_create_for_interesting(self):
        """
        Test creation for interesting article
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "feedback": "Esto apesta",
            "comment_labels": [
                comment_label(comm.id, is_hateful=bool(i % 2))
                for i, comm in enumerate(self.article.comment_set.all())
            ],
        }, assignment=True)

        assert serializer.is_valid()
        article_label = serializer.save()

        self.assertEqual(article_label.feedback, "Esto apesta")
        self.assertEqual(
            article_label.comment_labels.count(),
            self.article.comment_set.count()
        )

    def test_check_metadata_is_saved(self):
        """
        Test metadata
        """
        serializer = self.create_serializer({
            "is_interesting": False,
            "metadata": "{some_random: 'metadata'}"
        }, assignment=True)

        assert serializer.is_valid()
        article_label = serializer.save()

        assert article_label.metadata == "{some_random: 'metadata'}"

    def test_check_types(self):
        """
        Test creation for interesting article
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                comment_label(comm.id, is_hateful=bool(i % 2), types=[
                    "MUJER", "LGBTI", "POLITICA"])
                for i, comm in enumerate(self.article.comment_set.all())
            ],
        }, assignment=True)

        serializer.is_valid()
        article_label = serializer.save()
        # reload
        article_label = self.article.labels.first()

        for label in article_label.comment_labels.all():
            if not label.is_hateful:
                continue
            assert label.against_women
            assert label.against_lgbti
            assert label.against_political
            assert not label.against_race
            assert not label.against_poor
            assert not label.against_disabled

    def test_assignment_is_done_after_creating(self):
        """
        Test creation for interesting article
        """
        serializer = self.create_serializer({
            "is_interesting": True,
            "comment_labels": [
                comment_label(comm.id) for comm in self.article.comment_set.all()
            ],
        }, assignment=True)

        assert serializer.is_valid()
        serializer.save()

        assignment = self.article.assignment_set.get(user=self.user)

        assert assignment.done


class CommentLabelForCreationSerializerTest(TestCase):
    """
    Tests for validation and save of ArticleLabelSerializer
    """
    def setUp(self):
        self.article = ArticleFactory(create_comments__num_comments=5)
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )

    def test_if_not_hateful_is_valid(self):
        """
        Test if comment label is not hateful
        """
        serializer = CommentLabelForCreationSerializer(
            data={
                "comment": 1,
                "is_hateful": False,
                "calls_for_action": False,
                "types": []
            }
        )

        assert serializer.is_valid()

    def test_if_not_hateful_and_type_not_empty_is_not_valid(self):
        """
        Test if comment label is not hateful and type is not empty
        """
        serializer = CommentLabelForCreationSerializer(
            data={
                "comment": 1,
                "is_hateful": False,
                "calls_for_action": False,
                "types": ["RACISMO"]
            }
        )

        assert not serializer.is_valid()

    def test_if_not_hateful_calls_for_action_must_be_false(self):
        """
        Test if comment label is not hateful and type is not empty
        """
        serializer = CommentLabelForCreationSerializer(
            data={
                "comment": 1,
                "is_hateful": False,
                "calls_for_action": True,
                "types": []
            }
        )

        assert not serializer.is_valid()

    def test_if_hateful_and_type_is_set_it_is_valid(self):
        """
        Test if comment label is not hateful and type is not empty
        """
        serializer = CommentLabelForCreationSerializer(
            data={
                "comment": 1,
                "is_hateful": True,
                "calls_for_action": False,
                "types": ["RACISMO"]
            }
        )

        assert serializer.is_valid()

    def test_if_hateful_and_type_is_invalid_it_is_not_valid(self):
        """
        Test if comment label is not hateful and type is not empty
        """
        serializer = CommentLabelForCreationSerializer(
            data={
                "comment": 1,
                "is_hateful": True,
                "calls_for_action": False,
                "types": ["INVALID"]
            }
        )

        assert not serializer.is_valid()


    def test_if_hateful_with_many_types(self):
        """
        Test if comment label is not hateful and type is not empty
        """
        serializer = CommentLabelForCreationSerializer(
            data={
                "comment": 1,
                "is_hateful": True,
                "calls_for_action": False,
                "types": ["RACISMO", "LGBTI"]
            }
        )

        assert serializer.is_valid()
