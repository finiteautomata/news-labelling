#from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
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
        Check we have to log in first
        """

        art = ArticleFactory()
        comments = CommentFactory.create_batch(5, article=art)

        url = reverse("article-label", args=[art.id])

        req = {comm.id: {
            "hateful": 1
        } for comm in art.comment_set.all()}

        resp = self.client.post(url, req, format='json')

        for comment in comments:
            comment_url = reverse("comment-detail", args=[comment.id])
