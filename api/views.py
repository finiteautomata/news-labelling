from django.urls import reverse
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from .models import Article, Comment
from .serializers import ArticleSerializer, CommentSerializer

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
        article = self.get_object()

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
