from django.contrib.auth.models import User
from django.db import models, transaction
import django.dispatch
from .article import Article
from .comment import Comment
from .article_label import ArticleLabel
from django.core.exceptions import ValidationError
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
    comments = models.ManyToManyField(Comment, through="AssignmentComment")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    skippable = models.BooleanField(default=True)

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
        # Must delete ArticleLabel if one

        assignment_undone.send(sender=self.__class__, assignment=self)

    @property
    def article_label(self):
        return self.user.article_labels.get(article=self.article)

    def remove_label(self):
        """
        Delete label for this assignment
        """
        if self.done:
            return self.article_label.delete()

    def set_comments(self, comments):
        """
        Set whitelist of comments
        """
        with transaction.atomic():
            for comment in comments:
                AssignmentComment.objects.create(
                    comment=comment,
                    assignment=self,
                )

    def comments_to_label(self):
        """
        Get comments to be labeled

        If a whitelist => use that whitelist
        If no whitelist => use all comments from article
        """

        if self.comments.count() > 0:
            return self.comments.all()
        return self.article.comment_set.all()

    def reassign_for(self, another_assignment, only_comments=True):
        """
        Reassign when skipped
        """

        if not self.done or self.article_label.is_interesting:
            raise ValueError("Should be a skipped assignment")

        if not another_assignment.done or not another_assignment.article_label.is_interesting:
            raise ValueError("Should reassign wrt an annotated assignment")

        with transaction.atomic():
            if only_comments:
                annotated_label = another_assignment.article_label
                comments_to_reassign = [
                    comment_label.comment
                    for comment_label in annotated_label.comment_labels.all()
                    if comment_label.is_hateful
                ]

                if len(comments_to_reassign) > 0:
                    self.remove_label()
                    self.skippable = False
                    self.save(update_fields=["skippable"])
                    self.comments.set(comments_to_reassign)
        return self.refresh_from_db()

class AssignmentComment(models.Model, Completable):
    """
    Assignment to comments relationship model
    """

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('assignment', 'comment')

    def clean(self):
        """
        Model validation
        """
        if self.comment.article_id != self.assignment.article_id:
            raise ValidationError("Comment should match Assignment's article")


    def save(self, *args, **kwargs):
        """
        Override save to call Clean
        """
        self.clean()
        return super().save(*args, **kwargs)


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
