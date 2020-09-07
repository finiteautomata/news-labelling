from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for User class
    """

    class Meta:
        model = Article
        fields = ['title', 'tweet_id', 'text', 'url', 'user', 'body']
