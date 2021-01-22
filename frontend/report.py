import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
import pandas as pd
from api.models import Assignment, ArticleLabel, BatchAssignment, Batch


class AnnotationReport:
    """
    Calculates report
    """

    def __init__(self, users):
        """
        Constructor

        users: list of users to be considered
        """
        self.users = users

    def user_reports(self):
        """
        Iterable
        """
        report = {
            u.username: {
                "assignments": 0,
                "assignments_left": 0,
                "labeled_articles": 0,
                "labeled_articles_last_hours": 0,
                "skipped_articles": 0,
                "labeled_comments": 0,
                "time": 0,
                "username": u.username,
            }
            for u in self.users
        }

        for assignment in Assignment.objects.select_related('user'):
            username = assignment.user.username

            if username in report:
                report[username]["assignments"] += 1

                if not assignment.done:
                    report[username]["assignments_left"] += 1

        three_hours_ago = timezone.now() - timedelta(hours=3)

        for article_label in ArticleLabel.objects.select_related('user'):
            username = article_label.user.username

            if username in report:
                if article_label.is_interesting:
                    report[username]["labeled_articles"] += 1

                    if article_label.created_at > three_hours_ago:
                        report[username]["labeled_articles_last_hours"] += 1
                else:
                    report[username]["skipped_articles"] += 1

                report[username]["labeled_comments"] += article_label.comment_labels.count()

            metadata = json.loads(article_label.metadata)
            end = datetime.strptime(metadata["end_time"], '%Y-%m-%dT%H:%M:%S.%fZ')
            start = datetime.strptime(metadata["start_time"], '%Y-%m-%dT%H:%M:%S.%fZ')

            report[username]["time"] += (end - start).seconds

        for username, user_report in report.items():
            user_report["time"] = user_report["time"] / 3600
            yield user_report

    def batch_report(self):
        """
        Calculate batch report
        """

        usernames = [u.username for u in self.users]
        df = pd.DataFrame(columns=usernames)

        users = User.objects.filter(username__in=usernames)

        for batch in Batch.objects.all():
            for user in users:
                if batch.is_assigned_to(user):
                    batch_assignment = BatchAssignment(batch, user)

                    if batch_assignment.done:
                        value = "completed"
                    else:
                        completed = batch_assignment.completed_articles
                        to_be_done = batch_assignment.assignments.count()

                        value = f"progressing ({completed}/{to_be_done})"
                    df.loc[batch.name, user.username] = value

        df.fillna("na", inplace=True)

        idx = df.index
        order = ["training"] + sorted(idx.difference(["training"]), key=lambda x: int(x))

        for batch_name, rec in df.loc[order].iterrows():
            yield [batch_name, [rec[u] for u in usernames]]


    def feedbacks(self):
        """
        Return feedbacks
        """

        feedback_labels = ArticleLabel.objects.exclude(feedback="").order_by("-created_at")

        for feedback in feedback_labels:
            yield {
                "date": feedback.created_at,
                "user": feedback.user,
                "text": feedback.feedback,
                "article": feedback.article,
            }



