#from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .factories import ArticleFactory
from .mixins import AuthenticationMixin


class CommentViewTest(APITestCase, AuthenticationMixin):
    """
    API Test
    """

    def setUp(self):
        self.create_user_and_client()

        self.article = ArticleFactory(create_comments__num_comments=5)
        self.comment = self.article.comment_set.first()
        comment_id = self.comment.id
        self.url = reverse("comment-detail", args=[comment_id])

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

    def test_returns_right_things(self):
        """
        Check response has fields
        """
        self.login()

        response = self.get_comment()
        comment_ret = response.data

        for arg in ['text', 'tweet_id', 'user_id']:
            self.assertIn(arg, comment_ret)
            self.assertEqual(comment_ret[arg], getattr(self.comment, arg))

    def test_labels_are_empty(self):
        """
        Check comment has no labels when created
        """

        self.login()

        response = self.get_comment()
        comment_ret = response.data

        self.assertCountEqual(comment_ret["labels"], [])
