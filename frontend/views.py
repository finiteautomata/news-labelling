from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from api.models import Article, Assignment, CommentLabel, ArticleLabel, Batch, Comment
from api.metrics import AgreementCalculator
from .ranking import RankingCalculator
from .report import AnnotationReport

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
        assignment = get_object_or_404(Assignment, article=article, user=request.user)

        return render(request, 'articles/show.html', {
            "article": article,
            "assignment": assignment,
            "hate_speech_types": CommentLabel.HATE_SPEECH_TYPES,
            "comments": assignment.comments_to_label(),
        })

class LabelView(LoginRequiredMixin, View):
    """
    Show user labels
    """
    def get(self, request, username, article_pk):

        article = get_object_or_404(Article, pk=article_pk)
        label = get_object_or_404(ArticleLabel,
            user__username=username,
            article=article,
        )

        if not request.user.is_staff and request.user != label.user:
            return redirect("index")

        hate_speech_types = [t[0] for t in CommentLabel.HATE_SPEECH_TYPES]

        return render(request, 'labels/show.html', {
            "article": article,
            "username": username,
            "article_label": label,
            "hate_speech_types": hate_speech_types,
        })

class UserView(LoginRequiredMixin, View):
    """
    User view for annotators
    """
    @method_decorator(staff_member_required)
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        article_labels = user.article_labels.all()

        return render(request, 'users/show.html', {
            "user": user,
            "article_labels": article_labels,
        })

class BatchView(LoginRequiredMixin, View):
    """
    Batch View
    """

    def get_agreements_report(self, batch, users):
        """
        Return
        """
        calculator = AgreementCalculator(batch=batch, users=users)

        report = {}
        categories = ["HATE", "CALLS"] + list(CommentLabel.type_mapping)

        for category in categories:
            report[category] = calculator.get_category_report(category)

        return report

    @method_decorator(staff_member_required)
    def get(self, request, batch_name):
        batch = get_object_or_404(Batch, name=batch_name)
        users = [u for u in User.objects.exclude(username="jmperez") if batch.is_assigned_to(u)]

        num_comments = Comment.objects.filter(article__batch=batch).count()

        return render(request, 'batches/show.html', {
            "batch": batch,
            "num_comments": num_comments,
            "report": self.get_agreements_report(batch, users),
            "users": users,
        })

class DashboardView(LoginRequiredMixin, View):
    """
    User index
    """

    @method_decorator(staff_member_required)
    def get(self, request):
        """
        Show index
        """
        users = User.objects.all()

        # Get only annotators
        users = [u for u in users if u.assignment_set.count() > 0]

        report = AnnotationReport(users)
        return render(request, 'users/index.html', {
            "report": report,
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
