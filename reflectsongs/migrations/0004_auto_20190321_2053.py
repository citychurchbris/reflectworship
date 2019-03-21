# Generated by Django 2.1.5 on 2019-03-21 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reflectsongs', '0003_auto_20190306_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='authors',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='song',
            name='ccli_number',
            field=models.CharField(default='', max_length=200, verbose_name='CCLI Number'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='setlist',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
