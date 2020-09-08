from rest_framework import serializers
from .models import Article, Comment, CommentLabel


class CommentLabelSerializer(serializers.ModelSerializer):
    """
    Serializer for comment label class
    """

    class Meta:
        """
        Meta class
        """
        model = CommentLabel
        fields = ['is_hateful']

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comment class
    """
    class Meta:
        """
        Meta class
        """
        model = Comment
        fields = ['text', 'user_id', 'tweet_id', 'created_at', 'labels']

    labels = CommentLabelSerializer(many=True, read_only=True)

class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for User class
    """
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')

    class Meta:
        """
        Meta class
        """
        model = Article
        fields = ['title', 'tweet_id', 'text', 'url', 'user', 'body', 'comments', 'created_at']
