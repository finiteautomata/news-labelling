from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from api.models import Article


class Index(LoginRequiredMixin, View):
    """
    Base index page
    """
    def get(self, request):
        """
        GET index
        """
        return render(request, "index.html")

class ArticleView(LoginRequiredMixin, View):
    """
    Article show
    """
    def get(self, request, pk=None):
        """
        GET article
        """
        article = get_object_or_404(Article, pk=pk)

        return render(request, 'articles/show.html', {
            "article": article,
        })
