# Generated by Django 3.1.5 on 2021-01-13 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_auto_20210108_0603'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchassignment',
            name='completed_articles',
            field=models.IntegerField(default=0),
        ),
    ]