# Generated by Django 2.1.5 on 2019-03-06 21:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reflectsongs', '0002_setlist_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='setlist',
            unique_together={('date', 'name', 'site')},
        ),
    ]