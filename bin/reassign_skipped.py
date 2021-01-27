import os
import sys
from collections import defaultdict
import fire
import django

sys.path.append(".")
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_labelling.settings'
django.setup()

from django.db import transaction
from api.models import Article, ArticleLabel, Assigner


def reassign_skipped(batch_name):
    """
    Assign batch to user
    """

    query = {
        "is_interesting": False,
        "article__batch__name": batch_name
    }

    skipped_labels = ArticleLabel.objects.filter(**query).prefetch_related(
        'article', 'user'
    )

    assigner = Assigner()
    reassigned_articles = 0
    total_count = defaultdict(int)
    with transaction.atomic():
        for skipped_label in skipped_labels:
            article = skipped_label.article
            user = skipped_label.user
            if article.labels.filter(is_interesting=True).exists():
                """
                So, anyone annotated this => reassign
                """
                assignment = assigner.assign(article, user, reassign=True)

                if not assignment.done:
                    reassigned_articles += 1
                    new_comments = assignment.comments_to_label().count()
                    total_count[user] += new_comments

    print("Reassigned articles")
    print(reassigned_articles)
    print("Comments to be labelled per user")
    print(total_count)

if __name__ == '__main__':
    fire.Fire(reassign_skipped)
