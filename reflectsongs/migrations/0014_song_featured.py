# Generated by Django 2.2.2 on 2019-07-25 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reflectsongs', '0013_site_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='featured',
            field=models.BooleanField(default=False, help_text='Featured songs appear at the top of the homepage*New song* listings'),
        ),
    ]
