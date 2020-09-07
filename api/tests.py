#from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Article
from .factories import ArticleFactory



class ArticleViewTest(APITestCase):
    """
    API Test
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )

        self.url = reverse("article-list")

    def login(self):
        """
        Logs user in
        """
        resp = self.client.login(username="test", password="test")
        assert resp

    def test_not_accesible_if_not_logged(self):
        """
        Check we have to log in first
        """
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_accessible_if_logged(self):
        """
        Test HTTP ok if logged
        """
        self.login()

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
