# Generated by Django 2.2.2 on 2019-07-24 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reflectsongs', '0012_auto_20190724_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='slug',
            field=models.SlugField(null=True),
        ),
    ]
