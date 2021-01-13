from django.contrib.auth.models import User
from django.db import models
import django.dispatch
from .article import Article
from .article_label import ArticleLabel
from django.db.models.signals import post_delete, post_save
from django.core.exceptions import ObjectDoesNotExist
from .mixins import Completable

assignment_done = django.dispatch.Signal()
assignment_undone = django.dispatch.Signal()

# Create your models here.
class Assignment(models.Model, Completable):
    """
    Object linking user to articles


    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def next_assignment_of(cls, user):
        """
        Returns next assignment of user
        """
        return cls.objects.filter(user=user, done=False).first()


    class Meta:
        unique_together = ('user', 'article')

    def after_complete(self):
        """
        Send signal after completion
        """
        assignment_done.send(sender=self.__class__, assignment=self)

    def after_undo(self):
        """
        Send signal after undo
        """
        assignment_undone.send(sender=self.__class__, assignment=self)


def undo_assignment_on_label_delete(sender, instance, **kwargs):
    """
    If label is deleted => undo the assignment
    """
    user = instance.user
    article = instance.article
    try:
        assignment = Assignment.objects.get(user=user, article=article)
        assignment.undo()
    except ObjectDoesNotExist:
        # For some reason, assignment was already deleted
        # This happens, for instance, when deleting articles!
        # TODO: change this
        print("Warning: Assignment deleted before ArticleLabel")



def complete_assignment(sender, instance, created, raw, **kwargs):
    """
    After article label is created => complete assignment
    """
    if not raw and created:
        user = instance.user
        article = instance.article
        assignment = Assignment.objects.get(user=user, article=article)

        assignment.complete()


post_save.connect(complete_assignment, sender=ArticleLabel)
post_delete.connect(undo_assignment_on_label_delete, sender=ArticleLabel)
