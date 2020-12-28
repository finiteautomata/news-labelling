from django.contrib.auth.models import User
from django.db import models
from .article import Article
from .article_label import ArticleLabel
from django.db.models.signals import post_delete, post_save

# Create your models here.
class Assignment(models.Model):
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

    def complete(self):
        """
        Set as done
        """
        if self.done:
            # Raise if already completed
            raise ValueError("Assignment already completed")
        self.done = True
        self.save()

    def undo(self):
        """
        Undo!
        """
        if not self.done:
            # Raise if already completed
            raise ValueError("Assignment not done")
        self.done = False
        self.save()


    class Meta:
        unique_together = ('user', 'article')


def undo_assignment_on_label_delete(sender, instance, **kwargs):
    user = instance.user
    article = instance.article
    assignment = Assignment.objects.get(user=user, article=article)

    assignment.undo()



def complete_assignment(sender, instance, created, raw, **kwargs):
    if not raw and created:
        user = instance.user
        article = instance.article
        assignment = Assignment.objects.get(user=user, article=article)

        assignment.complete()


post_save.connect(complete_assignment, sender=ArticleLabel)
post_delete.connect(undo_assignment_on_label_delete, sender=ArticleLabel)
