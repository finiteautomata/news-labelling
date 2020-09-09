from rest_framework.test import APIClient
from django.contrib.auth.models import User

class AuthenticationMixin:
    """
    Creates user and login function
    """

    def create_user_and_client(self):
        """
        Setup mixin
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test",
            password="test",
        )

    def login(self):
        """
        Logs user in
        """
        resp = self.client.login(username="test", password="test")
        assert resp
