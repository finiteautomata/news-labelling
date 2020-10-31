from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from api.models import Article, Assignment, CommentLabel, ArticleLabel
from .ranking import RankingCalculator


class Index(LoginRequiredMixin, RankingCalculator, View):
    """
    Base index page
    """

    def get(self, request):
        """
        GET index
        """
        completed_articles = request.user.assignment_set.filter(done=True).count()
        return render(request, "index.html", {
            "completed_articles": completed_articles,
            "ranking": self.fake_ranking_for(request.user),
        })

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
            "hate_speech_types": CommentLabel.HATE_SPEECH_TYPES,

        })

class CompletedView(LoginRequiredMixin, View):
    """
    You completed it all!
    """

    def get(self, request):
        """
        GET completed
        """
        return render(request, 'articles/completed.html')

class NextArticleView(LoginRequiredMixin, View):
    """
    View for next assignment
    """

    def get(self, request):
        """
        GET next view
        """
        next_assignment = Assignment.next_assignment_of(request.user)

        if next_assignment:
            # Ok, next assignment, redirect there
            return redirect('article_view', pk=next_assignment.article.id)
        return redirect('completed')
