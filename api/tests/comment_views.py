#from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .factories import ArticleFactory, CommentFactory
from ..serializers import ArticleSerializer


class CommentViewSetTest(APITestCase):
    """
    API Test
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )
        self.article = ArticleFactory(create_comments__num_comments=5)
        comment_id = self.article.comment_set.first().id
        self.url = reverse("comment-detail", args=[comment_id])

    def login(self):
        """
        Logs user in
        """
        resp = self.client.login(username="test", password="test")
        assert resp

    def get_comment(self):
        """
        Get comment from REST API
        """
        return self.client.get(self.url)


    def test_not_accesible_if_not_logged(self):
        """
        Check we have to log in first
        """

        response = self.get_comment()
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_get_comment(self):
        """
        Check we have to log in first
        """

        self.login()

        response = self.get_comment()
        assert response.status_code == status.HTTP_200_OK
