import random
import datetime
from django.contrib.auth.models import User
from api.models import Assignment, CommentLabel, ArticleLabel

class RankingCalculator:
    """
    Calculates rankings
    """
    def ranking(self):
        """
        Calculates ranking
        """
        ranking = {u.username: {"articles": 0, "comments": 0} for u in User.objects.all()}

        for article_label in ArticleLabel.objects.select_related('user'):
            username = article_label.user.username
            ranking[username]["articles"] += 1

        for comment_label in CommentLabel.objects.select_related('article_label'):
            # N+1, replace!
            username = comment_label.article_label.user.username
            ranking[username]["comments"] += 1

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
        # Si no tiene assignments, no le miento :-)
        if Assignment.next_assignment_of(user):

            num_assigned = Assignment.objects.filter(user=user).count()
            num_done = Assignment.objects.filter(user=user, done=True).count()
            username = user.username
            random.seed(datetime.datetime.today().day)

            # Le sumo a todes!
            for other_user, values in ranking.items():
                if other_user != username and values["articles"] < 25:
                    new_articles = random.randint(2, 5)
                    new_comments = new_articles * 50
                    values["articles"] += new_articles
                    values["comments"] += new_comments

            users_below = {
                u:v for u, v in ranking.items()
                if v["comments"] < ranking[username]["comments"]
            }

            if users_below:
                # Agarro otros y los pongo arriba
                users_will_put_up_in_ranking = random.sample(
                    users_below.keys(),
                    min(3, len(users_below)
                ))

                for other_user in users_will_put_up_in_ranking:
                    values = ranking[other_user]
                    new_articles = random.randint(num_done+1, num_assigned)
                    new_comments = (new_articles - num_done) * 50

                    values["articles"] = new_articles
                    values["comments"] = ranking[username]["comments"] + new_comments

        return sorted(
            list(ranking.items()),
            key=lambda x: x[1]["comments"], reverse=True
        )
