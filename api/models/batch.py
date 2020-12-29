from django.db import models, transaction
from api.models import Article, Assignment, assignment_done
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .mixins import Completable

# Create your models here.
class Batch(models.Model):
    """
    Batch model
    """
    name = models.CharField(max_length=300, blank=False, unique=True)
    users = models.ManyToManyField(User, through="BatchAssignment")

    @classmethod
    def create_from_articles(cls, name, articles):
        """
        Convenience method for creating batch
        """
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
            batch_assignment = BatchAssignment.objects.create(batch=self, user=user)
            for art in self.articles.all():
                Assignment.objects.create(user=user, article=art)

        return batch_assignment

    def is_assigned_to(self, user):
        """
        Checks is assigned
        """
        return BatchAssignment.objects.filter(batch=self, user=user).exists()



class BatchAssignment(models.Model, Completable):
    """
    Batch to user relationship model
    """

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)


    class Meta:
        unique_together = ('user', 'batch')

def check_batch_completed(sender, assignment, **kwargs):
    """
    Check batch is complete after
    """
    user = assignment.user
    article = assignment.article
    # TODO: Fix this
    batch = article.batch

    try:
        batch_assignment = BatchAssignment.objects.get(user=user, batch=batch)

        done_assignments = Assignment.objects.filter(
            done=True,
            article__in=batch.articles.all(),
            user=user
        ).count()

        if done_assignments == batch.articles.count():
            batch_assignment.complete()

    except ObjectDoesNotExist:

        print(f"No batch assignment of {user.username} and {batch}")


assignment_done.connect(check_batch_completed, sender=Assignment)
