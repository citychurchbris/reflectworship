# Generated by Django 2.1.5 on 2019-03-06 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reflectsongs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='setlist',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
