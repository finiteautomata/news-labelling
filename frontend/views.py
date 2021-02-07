import io
import urllib
import base64
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
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

matplotlib.use('Agg')

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
        article_labels = user.article_labels.prefetch_related(
            'article', 'article__batch').order_by('-created_at')

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

class FullAnalysisView(LoginRequiredMixin, View):
    """
    Analysis of all annotations so far
    """

    @property
    def users(self):
        if not hasattr(self, "_users"):
            self._users = User.objects.exclude(assignment=None)
        return self._users

    @property
    def articles(self):
        if not hasattr(self, "_articles"):
            self._articles = Article.objects.exclude(batch__name="training")
        return self._articles

    @property
    def calculator(self):
        if not hasattr(self, "_calculator"):
            self._calculator = AgreementCalculator(
                articles=self.articles,
                users=self.users
            )
        return self._calculator



    def get_agreements_report(self):
        """
        Return
        """
        report = {}
        categories = ["HATE", "CALLS"] + list(CommentLabel.type_mapping)

        for category in categories:
            report[category] = self.calculator.get_agreement(category)

        return report

    def save_plot_as_bytes_io(self):
        """
        Saves current image
        """
        buf = io.BytesIO()
        buf.seek(0)
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded_image = base64.b64encode(buf.read())
        encoded_image = urllib.parse.quote(encoded_image)
        return encoded_image

    def get_pairwise_agreements(self):
        """
        Plot heatmap
        """
        usernames = sorted([u.username for u in self.users])

        agreements = pd.DataFrame(columns=usernames)
        users = self.users

        for i, u1 in enumerate(users):
            agreements.loc[u1.username, u1.username] = 1.0
            for j in range(i+1, len(users)):
                u2 = users[j]
                alpha, _ = self.calculator.get_agreement("hate", users=[u1.username, u2.username])
                agreements.loc[u1.username, u2.username] = alpha
                agreements.loc[u2.username, u1.username] = alpha
        agreements = agreements.astype(float)
        avg_agreement = (agreements.sum(axis=1)-1)/ (len(agreements)-1)

        agreements = agreements.loc[usernames, usernames]

        sns.heatmap(agreements, fmt=".2f", annot=True, cbar=False)

        return self.save_plot_as_bytes_io(), avg_agreement

    def bias_heatmap(self):
        """
        Calculates bias towards each class
        """
        non_normalized = self.calculator.get_bias_all(zscore=False)
        heatmap = self.calculator.get_bias_all(zscore=True)

        sns.heatmap(heatmap, annot=non_normalized, fmt=".3f", cbar=False)
        plt.title("Z-scores de annotator bias por clase")

        return self.save_plot_as_bytes_io()


    @method_decorator(staff_member_required)
    def get(self, request):
        #num_comments = Comment.objects.filter(article__batch=batch).count()
        bias_heatmap = self.bias_heatmap()
        agreement_heatmap, avg_agreement = self.get_pairwise_agreements()
        report = self.get_agreements_report()
        return render(request, 'dashboard/full_analysis.html', {
            "report": report,
            "users": self.users,
            "agreement_heatmap": agreement_heatmap,
            "avg_agreement": avg_agreement,
            "bias_heatmap": bias_heatmap,
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
