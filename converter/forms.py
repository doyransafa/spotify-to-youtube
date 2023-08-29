from django import forms
from django.core.validators import RegexValidator

class PlaylistForm(forms.Form):
    playlist_link = forms.CharField(
        label='',
        max_length=256, 
        validators=[
        RegexValidator(
            regex=r'^https://open\.spotify\.com/playlist/.*',
            message='Invalid Spotify playlist link.',
        ),
    ],
        widget=forms.TextInput(attrs={
            'pattern': r'^https://open\.spotify\.com/playlist/.*', 'title': 'Enter a valid Spotify playlist link, i.e: https://open.spotify.com/playlist/3gKydckJGh4K3xYPTUOgWE',
            'class': 'form-control form-control-lg border border-5 border-success',
            'placeholder' : 'Enter a Spotify playlist link...' ,
            }),
    )


