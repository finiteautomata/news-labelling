# Generated by Django 3.1.4 on 2020-12-15 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_articlelabel_metadata'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='metadata',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
