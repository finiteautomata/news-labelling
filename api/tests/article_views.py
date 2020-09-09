#from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .mixins import AuthenticationMixin
from .factories import ArticleFactory
from ..serializers import ArticleSerializer


class ArticleViewTest(APITestCase, AuthenticationMixin):
    """
    API Test
    """

    def setUp(self):
        self.create_user_and_client()

        self.url = reverse("api:article-list")

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

    def test_article_detail(self):
        """
        Test
        """
        self.login()
        art = ArticleFactory()
        url = reverse('api:article-detail', args=[art.id])

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        self.assertEqual(response.data["labels"], [])
        self.assertEqual(response.data["title"], art.title)
