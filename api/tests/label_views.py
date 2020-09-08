#from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .factories import ArticleFactory, CommentFactory
from .mixins import AuthenticationMixin


class LabelViewTest(APITestCase, AuthenticationMixin):
    """
    API Test
    """

    def setUp(self):
        self.create_user_and_client()

        self.url = reverse("article-list")
        self.login()

    def test_label_an_article_with_one_comment(self):
        """
        Check that after labelling it works ok
        """

        art = ArticleFactory()
        comments = CommentFactory.create_batch(5, article=art)

        url = reverse("article-label", args=[art.id])

        req = {comm.id: {
            "is_hateful": 1
        } for comm in art.comment_set.all()}

        resp = self.client.post(url, req, format='json')

        assert resp.status_code == status.HTTP_201_CREATED

        for comment in comments:
            comment_url = reverse("comment-detail", args=[comment.id])
            response = self.client.get(comment_url, format="json")

            self.assertEqual(
                response.data["labels"], [{
                    "is_hateful": 1
                }]
            )
