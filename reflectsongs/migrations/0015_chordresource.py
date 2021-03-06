# Generated by Django 2.2.2 on 2019-07-28 19:39

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('reflectsongs', '0014_song_featured'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChordResource',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('resource_type', models.CharField(choices=[('pdf', 'PDF'), ('chordpro', 'ChordPro')], max_length=200)),
                ('attachment', models.FileField(upload_to='chordresources')),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downloads', to='reflectsongs.Song')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
