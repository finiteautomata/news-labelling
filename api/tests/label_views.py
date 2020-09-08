#from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .factories import ArticleFactory
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

        self.url = reverse("article-list")
        self.login()

    def test_label_an_article_as_not_interesting(self):
        """
        Check that after labelling it works ok
        """

        art = ArticleFactory(create_comments__num_comments=5)
        url = reverse("article-label", args=[art.id])
        return
        req = { "is_interesting": 0 }

        resp = self.client.post(url, req, format='json')

        assert resp.status_code == status.HTTP_201_CREATED

        for comment in art.comment_set.all():
            comment_url = reverse("comment-detail", args=[comment.id])
            response = self.client.get(comment_url, format="json")

            self.assertEqual(
                response.data["labels"], [{
                    "is_hateful": 1
                }]
            )


    def test_label_an_article_with_comments_create_comment_label(self):
        """
        Check that after labelling it works ok
        """

        art = ArticleFactory(create_comments__num_comments=5)
        url = reverse("article-label", args=[art.id])

        req = { comm.id: {
            "is_hateful": 1
        } for comm in art.comment_set.all()}

        resp = self.client.post(url, req, format='json')

        assert resp.status_code == status.HTTP_201_CREATED

        for comment in art.comment_set.all():
            comment_url = reverse("comment-detail", args=[comment.id])
            response = self.client.get(comment_url, format="json")

            self.assertEqual(
                response.data["labels"], [{
                    "is_hateful": 1
                }]
            )
