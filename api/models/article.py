from django.db import models

# Create your models here.
class Article(models.Model):
    """
    Article class
    """
    title = models.CharField(max_length=300, blank=False)
    tweet_id = models.PositiveBigIntegerField(unique=True, db_index=True)
    text = models.CharField(blank=False, max_length=500)
    slug = models.CharField(blank=False, max_length=130, unique=True)
    url = models.CharField(blank=False, max_length=200)

    batch = models.ForeignKey(
        "Batch", null=True, on_delete=models.SET_NULL,
        related_name="articles",
    )
    user = models.CharField(max_length=40)
    body = models.TextField()
    created_at = models.DateTimeField()

    metadata = models.TextField()

    def __repr__(self):
        return f"@{self.user}: {self.title}"

    def __str__(self):
        return self.__repr__()
