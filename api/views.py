from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import Article
from .serializers import ArticleSerializer

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
    Viewset for users
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
