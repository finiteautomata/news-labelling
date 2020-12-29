# Generated by Django 3.1.4 on 2020-12-29 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20201229_1609'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batch',
            name='articles',
        ),
        migrations.AddField(
            model_name='article',
            name='batch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='api.batch'),
        ),
        migrations.DeleteModel(
            name='BatchArticle',
        ),
    ]