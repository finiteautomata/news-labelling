# Generated by Django 3.1.1 on 2020-10-23 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20200928_1439'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commentlabel',
            old_name='against_religion',
            new_name='against_political',
        ),
    ]
