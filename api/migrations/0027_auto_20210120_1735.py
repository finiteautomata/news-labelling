# Generated by Django 3.1.5 on 2021-01-20 17:35

import api.models.mixins
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_assignment_skippable'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.assignment')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.comment')),
            ],
            options={
                'unique_together': {('assignment', 'comment')},
            },
            bases=(models.Model, api.models.mixins.Completable),
        ),
        migrations.AddField(
            model_name='assignment',
            name='comment',
            field=models.ManyToManyField(through='api.AssignmentComment', to='api.Comment'),
        ),
    ]