from django.contrib import admin
from .models import Song, PlaylistSearch

# Register your models here.
admin.site.register((Song, PlaylistSearch))