# Generated by Django 2.2.2 on 2019-07-08 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reflectsongs', '0009_song_last_sync'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='ccli_number',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='CCLI Number'),
        ),
    ]
