from django.db import models, transaction, IntegrityError
from api.models import Article, Assignment, assignment_done, assignment_undone
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete
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
            batch_assignment = BatchAssignment.objects.create(batch=self, user=user)

            for article in self.articles.all():
                """
                Some articles might have been previously assigned -- in that case, skip
                """

                if user.assignment_set.filter(article=article).exists():
                    print(f"Assignment of '{article.title[:50]}' to {user.username} already exists -- skipping")
                else:
                    Assignment.objects.create(user=user, article=article)

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
    completed_articles = models.IntegerField(default=0)
    done = models.BooleanField(default=False)


    class Meta:
        unique_together = ('user', 'batch')

    def update(self):
        """
        Check status
        """
        completed_articles = Assignment.objects.filter(
            done=True,
            article__in=self.batch.articles.all(),
            user=self.user
        ).count()

        total_articles = self.batch.articles.count()

        self.completed_articles = completed_articles
        if completed_articles == total_articles:
            self.complete()
        elif self.done:
            self.undo()


def check_batch_status(sender, assignment, **kwargs):
    """
    Check batch is complete after
    """
    user = assignment.user
    article = assignment.article
    # TODO: Fix this
    batch = article.batch

    try:
        batch_assignment = BatchAssignment.objects.get(user=user, batch=batch)

        batch_assignment.update()
    except ObjectDoesNotExist:

        print(f"No batch assignment of {user.username} and {batch}")


assignment_done.connect(check_batch_status, sender=Assignment)
assignment_undone.connect(check_batch_status, sender=Assignment)
post_delete.connect(check_batch_status, sender=Assignment)
