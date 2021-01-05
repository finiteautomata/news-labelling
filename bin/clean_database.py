import os
import sys
import fire
import django

sys.path.append(".")
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_labelling.settings'
django.setup()

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from api.models import Batch, Article


def clean_database():
    """
    Removes everything but the users
    """

    article_count = Article.objects.count()
    batch_count = Batch.objects.count()

    print(f"Cleaning {article_count} articles and {batch_count} batches")

    confirmation = input("Are you sure? Type YES to confirm: ")

    if confirmation.upper() != "YES":
        print("Aborting")
        sys.exit(1)

    print(Article.objects.all().delete())
    print(Batch.objects.all().delete())



if __name__ == '__main__':
    fire.Fire(clean_database)
