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


def revoke_batch(
    username, batch_name):
    """
    Assign batch to user
    """
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        print(f"{username} is not a valid username")
        sys.exit(1)

    try:
        batch = Batch.objects.get(name=batch_name)
    except ObjectDoesNotExist:
        print(f"{batch_name} not a valid batch name")
        sys.exit(1)

    if batch.is_assigned_to(user):

        try:
            batch.revoke_from(user)
            print(f"Batch '{batch_name}' revoked from {username}")
        except ValueError as e:
            print(e)
            print(f"Cannot revoke {username} from batch {batch_name}")
            sys.exit(1)
    else:
        print(f"{batch_name} not assigned to {username}!")
        sys.exit(1)



if __name__ == '__main__':
    fire.Fire(revoke_batch)
