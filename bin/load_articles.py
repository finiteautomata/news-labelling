import os
import sys
import json
import random
import re
from datetime import datetime
import fire
import django
import ijson
from tqdm.auto import tqdm

sys.path.append(".")
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_labelling.settings'
print("Configuring django...")
django.setup()
print("Configuration ok")

from api.models import Article, Comment

url_regex = re.compile(
r"((?<=[^a-zA-Z0-9])(?:https?\:\/\/|[a-zA-Z0-9]{1,}\.{1}|\b)"
r"(?:\w{1,}\.{1}){1,5}"
r"(?:com|co|org|edu|gov|uk|net|ca|de|es|mil|iq|io|ac|ly|sm){1}"
r"(?:\/[a-zA-Z0-9]{1,})*)"
)

def parse_date(obj_dict):
    """
    Parse mongo date representation
    """
    return datetime.strptime(
        f"{obj_dict['created_at']['$date']}-0300",
        "%Y-%m-%dT%H:%M:%SZ%z",
    )

def get_elligible_comments(comment_list):
    """
    Get comments that meet some criteria to be labelled

    For instance: they have no URLs
    """

    elligible_comments = []

    for comment in comment_list:
        if not url_regex.search(comment["text"]):
            elligible_comments.append(comment)
    return elligible_comments

def create_article(art_dict, max_comments):
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

    elligible_comments = get_elligible_comments(art_dict["comments"])

    sampled_comments = random.sample(
        elligible_comments,
        min(max_comments, len(elligible_comments))
    )
    for comm in sampled_comments:
        args = {
            k:v for k, v in comm.items() if k in ["text", "user_id", "tweet_id"]
        }
        args["created_at"] = parse_date(comm)
        comm = Comment(**args)
        comm.article = art
        new_comments.append(comm)

    Comment.objects.bulk_create(new_comments)


def load_articles(json_path, max_comments=50, random_seed=2020):
    """
    Load articles and comments

    json_path: path
        path to json containing articles and comments
    """

    random.seed(random_seed)

    print(f"Loading articles from {json_path}")

    with open(json_path) as json_file:
        articles = ijson.items(json_file, 'item')

        for i, art_dict in enumerate(articles):
            create_article(art_dict, max_comments=max_comments)
            if i > 0 and (i+1) % 500 == 0:
                print(f"{i+1} articles processed")

    print(f"Now we have {Article.objects.count()} articles")

if __name__ == '__main__':
    fire.Fire(load_articles)
