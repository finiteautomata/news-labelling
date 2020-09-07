#from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .factories import ArticleFactory
from .serializers import ArticleSerializer


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

    def get_articles(self):
        """
        Get articles from API
        """
        return self.client.get(self.url)


    def test_not_accesible_if_not_logged(self):
        """
        Check we have to log in first
        """
        response = self.get_articles()

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_accessible_if_logged(self):
        """
        Test HTTP ok if logged
        """
        self.login()

        response = self.get_articles()

        assert response.status_code == status.HTTP_200_OK

    def test_returns_articles(self):
        """
        Test returns created articles
        """
        self.login()

        art1 = ArticleFactory()
        art2 = ArticleFactory()

        response = self.get_articles()
        articles = response.json()["results"]
        assert response.json()["count"] == 2
        self.assertCountEqual(
            articles,
            [ArticleSerializer(art).data for art in [art1, art2]]
        )
