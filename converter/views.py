import requests
import re
import json
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from .forms import PlaylistForm
from .models import PlaylistSearch, Song

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build


def playlist_search_view(request):
    if request.method == "POST":
        form = PlaylistForm(request.POST)

        if form.is_valid():
            playlist_link = form.cleaned_data["playlist_link"]
            playlist_id_list = re.findall(
                r"playlist/(\w*)/?", playlist_link)[0]

            playlist_details = search_playlist(playlist_id_list)
            playlist_pk = add_playlist_to_db(playlist_details, playlist_link)

            return redirect("playlist_details", pk=playlist_pk)

    else:
        form = PlaylistForm()
        playlists = PlaylistSearch.objects.all()

        playlists = playlists.order_by('-created_at', 'title')

        context = {"form": form, "playlists": playlists}

        if messages.get_messages(request):
            messages_to_display = [
                m.message for m in messages.get_messages(request)]
            context['messages'] = messages_to_display

        return render(request, "playlist_search.html", context)


def add_playlist_to_db(playlist_details, playlist_link):
    playlist_title = playlist_details.get("title")
    owner = playlist_details.get("owner")
    playlist_image = playlist_details.get("playlist_image")
    playlist_search, created = PlaylistSearch.objects.get_or_create(
        link=playlist_link,
        title=playlist_title,
        owner=owner,
        playlist_image=playlist_image,
    )

    # if created:
    song_list = playlist_details.get("song_list")
    for song_data in song_list:
        artists = song_data["track"]["artists"]
        artists_name = [artist["name"] for artist in artists]
        song_link = song_data["track"]["external_urls"]["spotify"]
        if len(song_data["track"]["album"]["images"]) == 0:
            album_image = ''
        else:
            album_image = song_data["track"]["album"]["images"][0]["url"]
        defaults = {
            "artist": ", ".join(artists_name),
            "title": song_data["track"]["name"],
            "album_image": album_image,
        }

        song, _ = Song.objects.update_or_create(
            song_link=song_link,
            defaults=defaults,
        )

        playlist_search.songs.add(song)

    return playlist_search.pk


def playlist_details_view(request, pk):
    playlist = get_object_or_404(PlaylistSearch, pk=pk)
    songs = playlist.songs.all()

    context = {
        "playlist": playlist,
        "songs": songs,
    }

    return render(request, "playlist_details.html", context)


def delete_playlist_view(request, pk):
    playlist = get_object_or_404(PlaylistSearch, pk=pk)

    playlist.delete()
    Song.objects.filter(playlist_search__isnull=True).delete()
    return redirect("playlist_search")


def remove_song_view(request, song_id, playlist_id):
    song = get_object_or_404(Song, pk=song_id)
    playlist = get_object_or_404(PlaylistSearch, pk=playlist_id)

    playlist.songs.remove(song)
    return redirect("playlist_details", pk=playlist_id)


def update_playlist_view(request, pk):
    playlist = get_object_or_404(PlaylistSearch, pk=pk)
    playlist_id = re.findall(r"playlist/(\w*)/?", playlist.link)[0]
    details = search_playlist(playlist_id)
    songs = details.get("song_list")

    for song_data in songs:
        artists = song_data["track"]["artists"]
        artists_name = [artist["name"] for artist in artists]
        song_link = song_data["track"]["external_urls"]["spotify"]
        if len(song_data["track"]["album"]["images"]) == 0:
            album_image = ''
        else:
            album_image = song_data["track"]["album"]["images"][0]["url"]
        defaults = {
            "artist": ", ".join(artists_name),
            "title": song_data["track"]["name"],
            "album_image": album_image,
        }

        song, _ = Song.objects.update_or_create(
            song_link=song_link,
            defaults=defaults,
        )
        playlist.songs.add(song)

    return redirect("playlist_details", pk=pk)


# might remove from views/
token_cache = {}


def get_spotify_access_token(client_id, client_secret):
    cached_token = token_cache.get(client_id)

    if cached_token and cached_token["expires_at"] > datetime.now():
        return cached_token["access_token"]

    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print('Acces token retrieval is successful.')
        return access_token
    else:
        error_message = (
            f"Access token request failed with status code: {response.status_code}"
        )
        raise Exception(error_message)

# might remove from views/


def search_playlist(playlist_id):
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_SECRET

    access_token = get_spotify_access_token(client_id, client_secret)
    fields = "name%2Cexternal_urls%28spotify%29%2Cimages%28url%29%2Cowner%28display_name%29%2Ctracks%28items%28track%28artists%28name%29%2Cname%2Cexternal_urls%2Calbum%28images%28url%29%29%29%29%29"

    BASE_URL = f"https://api.spotify.com/v1/playlists/"
    headers = {"Authorization": f"Bearer {access_token}"}

    url = f"{BASE_URL}{playlist_id}?fields={fields}"
    response = requests.get(url, headers=headers)

    print(url)

    if response.status_code == 200:
        data = response.json()

        song_list = data.get("tracks").get("items")
        title = data.get("name")
        owner = data.get("owner").get("display_name")
        if len(data.get("images")) > 0:
            playlist_image = data.get("images")[0].get("url")
        else:
            playlist_image = ''
        context = {
            "song_list": song_list,
            "title": title,
            "owner": owner,
            "playlist_image": playlist_image,
        }

        print('Search is successful')

        return context

    else:
        error_message = f"API request failed with status code: {response.status_code}"
        print(error_message)
        return response.status_code


def youtube_auth(request):
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    google_client_secrets_json = settings.GOOGLE_CLIENT_SECRETS_JSON
    google_client_secrets = json.loads(google_client_secrets_json)
    flow = InstalledAppFlow.from_client_config(google_client_secrets, SCOPES)
    credentials = flow.run_local_server(port=8080)
    request.session["youtube_credentials"] = credentials_to_dict(credentials)

    referring_url = request.META.get('HTTP_REFERER', '/')

    return redirect(referring_url)


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


def youtube_playlist(request, pk):
    youtube_credentials_dict = request.session.get("youtube_credentials", None)

    if not youtube_credentials_dict:
        return redirect("youtube_auth")

    youtube_credentials = Credentials(**youtube_credentials_dict)

    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version,
                    credentials=youtube_credentials)

    playlist = get_object_or_404(PlaylistSearch, pk=pk)
    song_list = playlist.songs.all()

    search_dict = youtube_search(youtube, song_list)

    playlist_name = playlist.title
    youtube_playlist = youtube_create_playlist(youtube, playlist_name)
    youtube_playlist_id = youtube_playlist.get('id')
    playlist.youtube_id = youtube_playlist_id
    playlist.save()

    youtube_populate_playlist(youtube, youtube_playlist_id, search_dict)

    return redirect("display_youtube_playlist", pk)


def display_youtube_playlist(request, pk):

    playlist = get_object_or_404(PlaylistSearch, pk=pk)
    youtube_id = playlist.youtube_id

    context = {"youtube_id": youtube_id, 'playlist': playlist}

    return render(request, 'youtube_playlist.html', context)


def youtube_search(youtube, song_list):
    search_dict = {}

    for song in song_list:
        song_name = f"{song.artist} - {song.title}"

        if song.youtube_id is not None:
            search_dict[song_name] = song.youtube_id

        else:
            search_response = (
                youtube.search()
                .list(q=song_name, type="video", part="id,snippet", maxResults=1)
                .execute()
            )

            video = search_response.get("items", None)
            if video:
                video_id = video[0]["id"]["videoId"]

                search_dict[song_name] = video_id
                song.youtube_id = video_id
                song.save()

    print(search_dict)

    return search_dict


def youtube_create_playlist(youtube, playlist_name):
    request = youtube.playlists().insert(
        part="snippet", body={"snippet": {"title": playlist_name}}
    )
    response = request.execute()

    return response


def youtube_populate_playlist(youtube, playlist_id, song_dict):

    for _, song_id in song_dict.items():
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": song_id},
                }
            },
        ).execute()
        print(f"Adding video to batch: {song_id}")


def spotify_auth(request):
    # scopes
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={settings.SPOTIFY_CLIENT_ID}"
        "&response_type=code"
        "&redirect_uri=http://localhost:8000/spotify-callback/"
        "&scope=playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public"
    )
    return redirect(auth_url)


def spotify_callback(request):
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error:
        messages.error(request, 'Spotify authentication is not succesfull!')
        return redirect('playlist_search')

    auth_url = "https://accounts.spotify.com/api/token"
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:8000/spotify-callback/',
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_SECRET,
    }
    response = requests.post(auth_url, data=data)
    access_token = response.json().get('access_token')

    request.session['spotify_access_token'] = access_token

    messages.success(request, 'Spotify authentication successful!')
    return redirect('playlist_search')


def spotify_add_all_playlists(request):
    if 'spotify_access_token' in request.session:
        access_token = request.session['spotify_access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        print(access_token)
    else:
        return redirect('spotify_auth')

    playlist_id_list = []

    while True:
        url = 'https://api.spotify.com/v1/me/playlists?offset=0&limit=50'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            playlists = data.get('items')
            for playlist in playlists:
                playlist_id_list.append(playlist.get('id'))
            if data.get('next'):
                url = data.get('next')
            else:
                break

        else:
            print(response.status_code)
            print(response.content)
            return redirect('playlist_search')

    for id in playlist_id_list:
        playlist_details = search_playlist(id)
        print(playlist_details)
        playlist_link = f'https://open.spotify.com/playlist/{id}'
        print(playlist_link)
        if type(playlist_details) is not dict:
            continue
        else:
            add_playlist_to_db(playlist_details, playlist_link)

    return redirect('playlist_search')
