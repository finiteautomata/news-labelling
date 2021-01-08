import os
import sys
import json
import random
import fire
import django

sys.path.append(".")
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_labelling.settings'
django.setup()

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from api.models import Article, ArticleLabel, Batch


def remove_labels(tweet_id, username=None):
    """
    Remove labels for
    """

    try:
        article = Article.objects.get(tweet_id=tweet_id)
    except ObjectDoesNotExist:
        print(f"{tweet_id} not a valid tweet id")
        sys.exit(1)

    try:
        if username:
            users = [User.objects.get(username=username)]
        else:
            users = User.objects.all()

    except ObjectDoesNotExist:
        print(f"{username} not valid user")
        sys.exit(1)


    labels = ArticleLabel.objects.filter(user__in=users, article=article)

    print(f"{labels.count()} article labels")
    usernames = [a.user.username for a in labels]

    print(f"Want to remove labels for this article for all users? {' - '.join(usernames)}")
    confirmation = input("Type YES to confirm: ")

    if confirmation.upper() != "YES":
        print("Exiting")
        sys.exit(1)

    out = labels.delete()
    print(out)



if __name__ == '__main__':
    fire.Fire(remove_labels)
