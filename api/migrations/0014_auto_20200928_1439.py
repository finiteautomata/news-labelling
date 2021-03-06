# Generated by Django 3.1.1 on 2020-09-28 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20200926_1902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commentlabel',
            name='type',
        ),
        migrations.AddField(
            model_name='commentlabel',
            name='against_disabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commentlabel',
            name='against_lgbti',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commentlabel',
            name='against_poor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commentlabel',
            name='against_race',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commentlabel',
            name='against_religion',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commentlabel',
            name='against_women',
            field=models.BooleanField(default=False),
        ),
    ]
