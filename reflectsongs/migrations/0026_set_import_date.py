# Generated by Django 2.2.10 on 2020-02-28 13:49

from django.db import migrations


def set_import_date(apps, schema_editor):
    Setlist = apps.get_model("reflectsongs", "Setlist")
    for setlist in Setlist.objects.all():
        if not setlist.import_date:
            setlist.import_date = setlist.date
            setlist.save()


class Migration(migrations.Migration):

    dependencies = [
        ('reflectsongs', '0025_auto_20200228_1323'),
    ]

    operations = [
        migrations.RunPython(
            set_import_date,
            migrations.RunPython.noop,
        ),
    ]
