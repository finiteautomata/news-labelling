from rest_framework import serializers
from .models import Article, Comment, CommentLabel, ArticleLabel


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

class CommentLabelForCreationSerializer(serializers.ModelSerializer):
    """
    This is an ad hoc serializer for validation
    """

    class Meta:
        """
        Meta class
        """
        model = CommentLabel
        fields = ['is_hateful', 'comment']


class ArticleLabelSerializer(serializers.Serializer):
    """
    Serializer for comment

    I don't use model serializer as it is fairly complex
    """

    is_interesting = serializers.BooleanField(required=True)
    comment_labels = CommentLabelForCreationSerializer(many=True, required=False)


    def validate(self, data, *args, **kwargs):
        """
        If not is_interesting => no labels
        """
        if not data["is_interesting"]:
            if len(data.get("comment_labels", {})) > 0:
                raise serializers.ValidationError("There must be no label if not interesting")
            return data
        """
        Now, it's interesting and has labels

        Check labels are assigned to each comment
        """
        comment_ids = {comm.id for comm in self.context['article'].comment_set.all()}
        label_ids = {comment_label["comment"].id for comment_label in data['comment_labels']}

        if comment_ids != label_ids:
            raise serializers.ValidationError(
                "Wrong comment ids -- every comment should have exactly one label"
            )

        """
        Check we have article and user
        """

        if not ('user' in self.context and 'article' in self.context):
            raise serializers.ValidationError(
                "Article and user must be set in context"
            )

        return data

    def create(self, validated_data):
        """
        Create ArticleLabel
        """
        comment_labels = validated_data.pop('comment_labels', [])
        article = self.context['article']
        user = self.context['user']

        article_label = article.labels.create(**validated_data, user=user)
        for comment_label in comment_labels:
            article_label.comment_labels.create(**comment_label)

        return article_label


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
    labels = ArticleLabelSerializer(many=True, read_only=True)
    class Meta:
        """
        Meta class
        """
        model = Article
        fields = [
            'title', 'tweet_id', 'text', 'url', 'user', 'body',
            'comments', 'created_at', 'labels',
        ]
