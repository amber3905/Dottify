from django import forms
from .models import Album, Song, Playlist


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'format', 'artist_name', 'release_date', 'retail_price', 'cover_image']


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'album', 'length']


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'owner', 'songs', 'visibility']
