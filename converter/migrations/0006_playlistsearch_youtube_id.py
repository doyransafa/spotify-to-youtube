# Generated by Django 4.2.4 on 2023-08-17 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("converter", "0005_playlistsearch_youtube_link_song_youtube_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="playlistsearch",
            name="youtube_id",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
