import random
import datetime
from django.contrib.auth.models import User
from api.models import Assignment, CommentLabel, ArticleLabel

fake_names = [
    "koalacansado",
    "cocodrilodundee",
    "montypython",
    "patonegro",
    "pangolinpreciso",
    "unicornioazul",
    "elsalmon",
    "winniepooh",
]

class RankingCalculator:
    """
    Calculates rankings
    """
    def ranking(self):
        """
        Calculates ranking
        """

        ranking = {
            u.username: {"articles": 0, "comments": 0}
            for u in User.objects.filter(assignment__isnull=False)
        }

        article_labels = ArticleLabel.objects.prefetch_related(
            'user', 'comment_labels'
        )
        for article_label in article_labels:
            username = article_label.user.username
            ranking[username]["articles"] += 1
            ranking[username]["comments"] += article_label.comment_labels.count()

        return ranking

    def sorted_ranking(self):
        """
        Returns ranking sorted by comments
        """
        return sorted(
            list(self.ranking().items()),
            key=lambda x: x[1]["comments"], reverse=True
        )

    def fake_ranking_for(self, user):
        """
        Creates a fake ranking for that user
        """
        ranking = self.ranking()
        if not user.is_staff:
            username = user.username
            random.seed(datetime.datetime.today().day)

            # Le sumo a todes!
            for other_user, values in ranking.items():
                if other_user != username and values["articles"] < 25:
                    new_articles = random.randint(2, 5)
                    new_comments = new_articles * 50
                    values["articles"] += new_articles
                    values["comments"] += new_comments


        ret = sorted(
            list(ranking.items()),
            key=lambda x: x[1]["comments"], reverse=True
        )

        if not user.is_staff:
            """
            Replace names!
            Change tuples to list to support assignment
            """

            ret = [list(p) for p in ret]
            i = 0
            for pair in ret:
                if pair[0] != user.username:
                    pair[0] = fake_names[i]
                    i += 1

        return ret
