from api.models import Assignment, ArticleLabel

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



        for username, user_report in report.items():
            yield user_report