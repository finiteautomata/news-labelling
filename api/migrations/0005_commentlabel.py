# Generated by Django 3.1.1 on 2020-09-08 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20200907_1353'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_hateful', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labels', to='api.comment')),
            ],
        ),
    ]