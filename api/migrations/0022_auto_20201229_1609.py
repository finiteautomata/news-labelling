# Generated by Django 3.1.4 on 2020-12-29 16:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0021_auto_20201228_2127'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='batcharticle',
            unique_together={('article', 'batch')},
        ),
        migrations.AlterUniqueTogether(
            name='batchassignment',
            unique_together={('user', 'batch')},
        ),
    ]
