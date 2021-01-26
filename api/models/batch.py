from django.db import models, transaction
from django.contrib.auth.models import User
from .assigner import Assigner
from . import Article, Assignment

# Create your models here.
class Batch(models.Model):
    """
    Batch model
    """
    name = models.CharField(max_length=300, blank=False, unique=True)

    @property
    def users(self):
        """
        Return users who have any assignment to this batch
        """
        return User.objects.filter(assignment__article__batch=self).distinct()

    @classmethod
    def create_from_articles(cls, name, articles):
        """
        Convenience method for creating batch
        """
        assert articles is not []
        with transaction.atomic():
            batch = cls(name=name)
            batch.save()

            for art in articles:
                art.batch = batch
                art.save()

        return batch

    def assign_to(self, user):
        """
        Assign batch to user
        """
        with transaction.atomic():
            assigner = Assigner()

            for article in self.articles.all():
                """
                Some articles might have been previously assigned -- in that case, skip
                """
                assigner.assign(article, user)

        return BatchAssignment(self, user)

    def revoke_from(self, user):
        """
        Revokes from user. If started, raises exception
        """

        with transaction.atomic():

            batch_assignment = BatchAssignment(self, user)

            if batch_assignment.completed_articles == 0:
                batch_assignment.assignments.delete()
            else:
                raise ValueError("Already started batch!")

    def is_assigned_to(self, user):
        """
        Checks is assigned
        """

        return user.assignment_set.filter(
            article__batch=self,
        ).exists()



class BatchAssignment:
    """
    Batch to user helper
    """
    def __init__(self, batch, user):
        """
        Constructor
        """
        self.user = user
        self.batch = batch


    @property
    def assignments(self):
        return self.user.assignment_set.filter(
            article__batch=self.batch,
        )

    @property
    def done(self):
        """
        Is assigned
        """
        return self.assignments.exists() and not self.assignments.filter(done=False).exists()

    @property
    def completed_articles(self):
        """
        Number of completed articles
        """
        return self.assignments.filter(done=True).count()
