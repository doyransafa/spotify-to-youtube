# Generated by Django 4.2.4 on 2023-08-15 00:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("converter", "0003_playlistsearch_owner_playlistsearch_playlist_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="song",
            name="playlist_search",
        ),
        migrations.AddField(
            model_name="song",
            name="playlist_search",
            field=models.ManyToManyField(
                related_name="songs", to="converter.playlistsearch"
            ),
        ),
    ]