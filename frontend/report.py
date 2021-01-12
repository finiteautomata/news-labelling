import json
from datetime import datetime
import pandas as pd
from api.models import Assignment, ArticleLabel, BatchAssignment


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


        for article_label in ArticleLabel.objects.select_related('user'):
            username = article_label.user.username

            if username in report:
                if article_label.is_interesting:
                    report[username]["labeled_articles"] += 1
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

        for batch_assignment in BatchAssignment.objects.all():
            user_name = batch_assignment.user.username
            if user_name in usernames:
                batch_name = batch_assignment.batch.name
                value = "completed" if batch_assignment.done else "progressing"
                df.loc[batch_name, user_name] = value

        df.fillna("na", inplace=True)

        for batch_name, rec in df.iterrows():
            yield [batch_name, [rec[u] for u in usernames]]


    def feedbacks(self):
        """
        Return feedbacks
        """

        feedback_labels = ArticleLabel.objects.exclude(feedback="")

        for feedback in feedback_labels:
            yield {
                "user": feedback.user,
                "text": feedback.feedback,
                "article": feedback.article,
            }

