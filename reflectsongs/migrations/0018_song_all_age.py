# Generated by Django 2.2.4 on 2019-09-11 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reflectsongs', '0017_auto_20190802_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='all_age',
            field=models.BooleanField(default=False, help_text='This song is recommended for all-age worship'),
        ),
    ]
