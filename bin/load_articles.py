import os
import sys
import json
from datetime import datetime
import fire
import django
from tqdm.auto import tqdm

sys.path.append(".")
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_labelling.settings'
print("Configuring django...")
django.setup()
print("Configuration ok")

from api.models import Article, Comment

def parse_date(obj_dict):
    """
    Parse mongo date representation
    """
    return datetime.strptime(
        f"{obj_dict['created_at']['$date']}-0300",
        "%Y-%m-%dT%H:%M:%SZ%z",
    )

def create_article(art_dict):
    """
    Create article and comments from article json
    """

    args = {
        k:v for k, v in art_dict.items()
        if k in ["title", "body", "text", "slug", "user", "tweet_id", "url"]
    }

    args["created_at"] = parse_date(art_dict)

    art = Article(**args)
    art.save()

    new_comments = []

    for comm in art_dict["comments"]:
        args = {
            k:v for k, v in comm.items() if k in ["text", "user_id", "tweet_id"]
        }
        args["created_at"] = parse_date(comm)
        comm = Comment(**args)
        comm.article = art
        new_comments.append(comm)

    Comment.objects.bulk_create(new_comments)


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
