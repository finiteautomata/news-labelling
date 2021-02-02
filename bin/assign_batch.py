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
from api.models import Batch


def assign_batch(
    username, batch_name):
    """
    Assign batch to user
    """

    try:
        batch = Batch.objects.get(name=batch_name)
    except ObjectDoesNotExist:
        print(f"{batch_name} not a valid batch name")
        sys.exit(1)

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        print(f"{username} is not a valid username")
        sys.exit(1)

    if batch.is_assigned_to(user):
        print(f"{batch_name} already assigned to {username}")
        print("Skipping")
        return

    batch_assignment = batch.assign_to(user)

    print(f"Batch '{batch_name}' assigned to {username}")
    summary = batch_assignment.summary
    print(f"Articles {summary['articles']} -- Comments {summary['comments']}")

if __name__ == '__main__':
    fire.Fire(assign_batch)
