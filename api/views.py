from django.urls import reverse
from django.db import transaction
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from .models import Article, Comment, ArticleLabel
from .serializers import ArticleSerializer, CommentSerializer, CommentLabelSerializer, ArticleLabelSerializer

@api_view(['GET'])
def api_root(request, format=None):
    """
    Entrypoint
    """
    return Response({
        'articles': reverse('article-list', request=request, format=format),
    })

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for Articles
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]


    @action(methods=['post'], detail=True, url_path="label", url_name="label")
    def label(self, request, pk=None):
        """
        Label an article and its comments
        """
        article = self.get_object()
        data = request.data

        serializer = ArticleLabelSerializer(data=data)

        if serializer.is_valid():
            serializer.save()


        with transaction.atomic():
            for comment_id, label_data in request.data.items():
                comment = article.comment_set.get(id=comment_id)

                serializer = CommentLabelSerializer(data=label_data)

                if serializer.is_valid():
                    serializer.save(comment=comment)

        return Response({}, status=status.HTTP_201_CREATED)

class CommentViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin):
    """
    Viewset for comments
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
