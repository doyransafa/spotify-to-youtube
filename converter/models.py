from django.db import models

# Create your models here.


class PlaylistSearch(models.Model):
    # playlist_id = models.CharField(max_length=256, primary_key=True)
    title = models.CharField(max_length=256, default='Untitled', null=True)
    link = models.URLField(max_length=256, unique=True)
    owner = models.CharField(max_length=256, null=True)
    playlist_image = models.URLField(max_length=256, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    youtube_link = models.URLField(max_length=200, null=True)
    youtube_id = models.CharField(max_length=200, null=True)

    def __str__(self) -> str:
        return self.title


class Song(models.Model):
    # song_id = models.CharField(max_length=256, primary_key=True)
    artist = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    song_link = models.URLField(max_length=150, unique=True)
    album_image = models.URLField(max_length=200)
    playlist_search = models.ManyToManyField(PlaylistSearch, related_name='songs')
    youtube_link = models.URLField(max_length=200, null=True)
    youtube_id = models.CharField(max_length=200, null=True)

    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"

