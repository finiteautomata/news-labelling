import json
from django.urls import reverse
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from .models import Article, Comment
from .serializers import ArticleSerializer, CommentSerializer, ArticleLabelSerializer

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
        data["metadata"] = json.dumps(data["metadata"]) if "metadata" in data else ""
        serializer = ArticleLabelSerializer(data=data, context={
            'article': article,
            'user': request.user,
        })

        if serializer.is_valid():
            serializer.save()

            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin):
    """
    Viewset for comments
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
