from django.urls import path
from .views import (
    playlist_search_view,
    playlist_details_view,
    delete_playlist_view,
    remove_song_view,
    update_playlist_view,
    youtube_auth,
    youtube_playlist,
    display_youtube_playlist,
    spotify_auth,
    spotify_callback,
    spotify_add_all_playlists,
)

urlpatterns = [
    path("", playlist_search_view, name="playlist_search"),
    path("playlist/<int:pk>", playlist_details_view, name="playlist_details"),
    path("playlist/delete/<int:pk>", delete_playlist_view, name="delete_playlist"),
    path("playlist/update/<int:pk>", update_playlist_view, name="update_playlist"),
    path(
        "playlist/generate_yotube/<int:pk>",
        youtube_playlist,
        name="generate_youtube_playlist",
    ),
    path(
        "playlist/youtube_playlist/<int:pk>",
        display_youtube_playlist,
        name="display_youtube_playlist",
    ),
    path(
        "playlist/<int:playlist_id>/song/<int:song_id>",
        remove_song_view,
        name="remove_song",
    ),
    path("youtube_auth/", youtube_auth, name="youtube_auth"),
    path("spotify_auth/", spotify_auth, name="spotify_auth"),
    path('spotify-callback/', spotify_callback, name='spotify_callback'),
    path('spotify_add_all_playlists/', spotify_add_all_playlists, name='spotify_add_all_playlists'),

]
