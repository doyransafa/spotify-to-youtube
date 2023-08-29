# spotify-to-youtube
## A Django project to create YouTube playlists based on Spotify playlists

## Project Demo Video:
# [YouTube Link]( https://youtu.be/xU_1QDqYgDU )

<img width="721" alt="image" src="https://github.com/doyransafa/spotify-to-youtube/assets/72417108/84ab80c6-5e67-49a5-9b81-47819c4c44f2">

## **Features:**

- **Add Spotify playlists with links**
  - This process doesn't require any authentication. Any Spotify playlist entered will be added to your playlists.
- **Add all playlists of authenticated users**
  - After users authenticate their Spotify profile, the app generates every playlist automatically and lists all of them.
- **Update playlist songs**
  - After creating playlists users can remove any song they want to include from the resulting YouTube playlist.
- **Generate a YouTube playlist**
  - With YouTube authentication, the application searches each title on YouTube and creates a private playlist with the same name and songs.

## **Notes:**
YouTube API requires extensive registration (privacy policy, terms of service etc.) in order to publish this app for general use. This project will only work if you create your own test app with credentials and register your Google account as a test user. You can add a .env file with SPOTIFY_CLIENT_ID, SPOTIFY_SECRET, and GOOGLE_CLIENT_SECRETS_JSON

## **Potential Improvements:**

- More extensive error handling. Right now program crashes if something goes wrong.
- Manual additions to the list.

## **Stack:**
- Django
- Bootstrap
- SQLite
