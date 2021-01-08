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

    articles = Article.objects.filter(tweet_id__in=tweet_ids)

    if articles.count() != len(tweet_ids):
        diff = len(tweet_ids) - articles.count()
        print(f"WARNING: There are {diff} tweet ids not present in {path}")

    batch = Batch.create_from_articles(name=batch_name, articles=articles)
    print(f"Created {batch.name} batch with {articles.count()} articles")
    return tweet_ids


def load_batches(random_seed=2020, remove=False, demo=False, interview=False, batch_size=50):
    random.seed(random_seed)

    article_ids = [art.tweet_id for art in Article.objects.all().only('tweet_id')]

    print(f"{len(article_ids)} articles")

    if remove:
        print("Remove existent batches?")
        confirmation = input("Write YES to confirm: ")
        if confirmation.upper() != "YES":
            print("Exiting")
            sys.exit(1)
        out = Batch.objects.all().delete()
        print(f"Deleted: {out}")

    if demo:
        load_batch_from_file("data/demo_ids.json", "demo")
    elif interview:
        load_batch_from_file("data/interview_ids.json", "interview")
    else:
        training_ids = load_batch_from_file("data/training_ids.json", "training")
        print("Creating other batches")
        print(f"Batch size {batch_size}")
        remaining_ids = [art_id for art_id in article_ids if art_id not in training_ids]

        random.shuffle(remaining_ids)
        """
        Create batch ids
        """
        batch_ids = [remaining_ids[i:i+batch_size] for i in remaining_ids[::batch_size]]

        batches = []

        with transaction.atomic():
            for i, ids in enumerate(batch_ids):
                articles = Article.objects.filter(tweet_id__in=ids)
                assert articles.count() == len(ids)
                batch = Batch.create_from_articles(str(i+1), articles)

                print(f"Batch {batch.name} created")
                batches.append(batch)

        print(f"{len(batches)} batches created for {len(remaining_ids)} articles")






if __name__ == '__main__':
    fire.Fire(load_batches)
