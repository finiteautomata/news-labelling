import os
import sys
sys.path.append(".")
import json
import fire
import pytz
import django
from datetime import datetime
from tqdm.auto import tqdm

os.environ['DJANGO_SETTINGS_MODULE'] = 'news_labelling.settings'
print("Configuring django...")
django.setup()
print("Configuration ok")

from api.models import Article


def create_article(art_dict):
    """
    Create article and comments from article json
    """

    args = {
        k:v for k, v in art_dict.items()
        if k in ["title", "body", "text", "slug", "user", "tweet_id", "url"]
    }

    args["created_at"] = datetime.strptime(
        f"{art_dict['created_at']['$date']}-0300",
        "%Y-%m-%dT%H:%M:%SZ%z",
    )

    art = Article(**args)

    art.save()

def load_articles(json_path):
    """
    Load articles and comments

    json_path: path
        path to json containing articles and comments
    """

    print(f"Loading articles from {json_path}")
    with open(json_path) as json_file:
        articles = json.load(json_file)

    print(f"Loaded {len(articles)} articles")

    for art_dict in tqdm(articles):
        create_article(art_dict)

    print(f"Now we have {Article.objects.count()} articles")

if __name__ == '__main__':
    fire.Fire(load_articles)
