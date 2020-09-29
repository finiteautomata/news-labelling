import os
import sys
import json
import random
import fire
import django
from tqdm.auto import tqdm

sys.path.append(".")
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_labelling.settings'
django.setup()

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from api.models import Article, Assignment


def assign_articles(
    username, ids_file=None, number_of_articles=None, random_seed=2020):
    """
    Load articles and comments

    json_path: path
        path to json containing articles and comments
    """

    random.seed(random_seed)

    if not number_of_articles and not ids_file:
        print("Must bring number_of_articles or ids_file")
        return

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        print(u"{username} is not a valid username")
        return

    if ids_file:
        with open(ids_file) as f:
            tweet_ids = json.load(f)

        print(f"Loaded {len(tweet_ids)} tweet ids")
        articles = Article.objects.filter(tweet_id__in=tweet_ids)
        print(f"Found {articles.count()} articles in database")
    else:
        articles = Article.objects.all()

    # Convert to list to sample
    articles = list(articles)
    if number_of_articles:
        articles = random.sample(
            articles,
            min(len(articles), number_of_articles)
        )

    for art in articles:
        user.assignment_set.create(article=art)

    print(f"User has now {user.assignment_set.count()} assignments")

if __name__ == '__main__':
    fire.Fire(assign_articles)
