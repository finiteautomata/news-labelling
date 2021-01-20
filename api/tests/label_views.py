#from django.test import TestCase
import datetime
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .factories import ArticleFactory, comment_label
from .mixins import AuthenticationMixin

class LabelViewTest(APITestCase, AuthenticationMixin):
    """
    API Test
    """

    def setUp(self):
        """
        Setup method
        """
        self.create_user_and_client()
        self.url = reverse("api:article-list")
        self.login()

    def test_label_an_article_as_not_interesting(self):
        """
        Check that after labelling it works ok
        """

        art = ArticleFactory(create_comments__num_comments=5)
        self.user.assignment_set.create(article=art)
        url = reverse("api:article-label", args=[art.id])

        now = datetime.datetime.utcnow()
        before = now - datetime.timedelta(hours=1)
        req = {
            "is_interesting": False,
            "metadata": {
                "start_time": str(before),
                "end_time": str(now)
            }
        }

        resp = self.client.post(url, req, format='json')
        assert resp.status_code == status.HTTP_201_CREATED

        response = self.client.get(reverse('api:article-detail', args=[art.id]))

        self.assertEqual(
            response.data["labels"],
            [{
                "is_interesting": False,
                "comment_labels": [],
                "metadata": json.dumps(req["metadata"]),
                "feedback": "",
            }]
        )

    def test_label_an_article_as_not_interesting_with_feedback(self):
        """
        Check that after labelling it works ok
        """

        art = ArticleFactory(create_comments__num_comments=5)
        self.user.assignment_set.create(article=art)
        url = reverse("api:article-label", args=[art.id])

        now = datetime.datetime.utcnow()
        before = now - datetime.timedelta(hours=1)
        req = {
            "is_interesting": False,
            "metadata": {
                "start_time": str(before),
                "end_time": str(now)
            },
            "feedback": "I don't like this",
        }

        resp = self.client.post(url, req, format='json')
        assert resp.status_code == status.HTTP_201_CREATED

        response = self.client.get(reverse('api:article-detail', args=[art.id]))

        self.assertEqual(
            response.data["labels"],
            [{
                "is_interesting": False,
                "comment_labels": [],
                "metadata": json.dumps(req["metadata"]),
                "feedback": req["feedback"],
            }]
        )


    def test_label_an_article_with_comments_create_comment_label(self):
        """
        Check that after labelling it works ok
        """

        art = ArticleFactory(create_comments__num_comments=5)
        self.user.assignment_set.create(article=art)
        url = reverse("api:article-label", args=[art.id])

        labels = [
            comment_label(
                comm.id,
                is_hateful=bool(i % 2 == 0),
                types=["RACISMO", "POBREZA"],
                calls_for_action=bool(i % 4 == 0),
            )
            for i, comm in enumerate(art.comment_set.all())
        ]

        now = datetime.datetime.utcnow()
        before = now - datetime.timedelta(hours=1)
        req = {
            "is_interesting": True,
            "comment_labels": labels,
            "metadata": {
                "start_time": str(before),
                "end_time": str(now)
            },
            "feedback": "A bit difficult"
        }

        resp = self.client.post(url, req, format='json')

        assert resp.status_code == status.HTTP_201_CREATED

        for exp_label, comment in zip(labels, art.comment_set.all()):
            comment_url = reverse("api:comment-detail", args=[comment.id])
            response = self.client.get(comment_url, format="json")
            exp_label.pop('comment')

            self.assertEqual(
                response.data["labels"], [exp_label]
            )


    def test_label_an_article_with_just_some_comments(self):
        """
        Check that after labelling it works ok
        """

        art = ArticleFactory(create_comments__num_comments=5)
        assignment = self.user.assignment_set.create(article=art)
        comments_to_label = list(art.comment_set.all()[:3])

        assignment.set_comments(comments_to_label)
        url = reverse("api:article-label", args=[art.id])

        labels = [
            comment_label(
                comm.id,
                is_hateful=bool(i % 2 == 0),
                types=["RACISMO", "POBREZA"],
                calls_for_action=bool(i % 4 == 0),
            )
            for i, comm in enumerate(comments_to_label)
        ]

        now = datetime.datetime.utcnow()
        before = now - datetime.timedelta(hours=1)
        req = {
            "is_interesting": True,
            "comment_labels": labels,
            "metadata": {
                "start_time": str(before),
                "end_time": str(now)
            },
            "feedback": "A bit difficult"
        }

        resp = self.client.post(url, req, format='json')

        assert resp.status_code == status.HTTP_201_CREATED

        for exp_label, comment in zip(labels, comments_to_label):
            comment_url = reverse("api:comment-detail", args=[comment.id])
            response = self.client.get(comment_url, format="json")
            exp_label.pop('comment')

            self.assertEqual(
                response.data["labels"], [exp_label]
            )