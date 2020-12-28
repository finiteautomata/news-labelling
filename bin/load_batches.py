import os
import sys
import json
import random
import fire
import django

sys.path.append(".")
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_labelling.settings'
django.setup()

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from api.models import Article, Assignment, Batch


def load_batch_from_file(path, batch_name):
    """
    Load batch from a JSON file containing an array of tweet ids
    """

    if Batch.objects.filter(name=batch_name).exists():
        print(f"Batch {batch_name} already exists -- skipping")
        return

    with open(path) as f:
        tweet_ids = json.load(f)

    batch = Batch(name=batch_name)
    batch.save()

    articles = Article.objects.filter(tweet_id__in=tweet_ids)

    if articles.count() != len(tweet_ids):
        diff = len(tweet_ids) - articles.count()
        print(f"WARNING: There are {diff} tweet ids not present in {path}")

    batch.articles.set(articles)
    print(f"Created {batch.name} batch with {articles.count()} articles")


def load_batches(random_seed=2020, remove_batches=False, demo=False):
    random.seed(random_seed)

    article_ids = [art.tweet_id for art in Article.objects.all().only('tweet_id')]

    print(f"{len(article_ids)} articles")

    if remove_batches:
        print("Remove existent batches?")
        confirmation = input("Write YES to confirm: ")
        if confirmation.upper() != "YES":
            print("Exiting")
            sys.exit(1)
        out = Batch.objects.all().delete()
        print(f"Deleted: {out}")

    if demo:
        load_batch_from_file("data/demo_ids.json", "demo")
    else:
        load_batch_from_file("data/interview_ids.json", "interview")






if __name__ == '__main__':
    fire.Fire(load_batches)
