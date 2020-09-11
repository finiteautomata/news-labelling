from django.contrib.auth.models import User
from django.db import models
from .article import Article

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

    class Meta:
        unique_together = ('user', 'article')
