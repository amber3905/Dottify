from django import forms
from .models import Album, Song, Playlist


class AlbumForm(forms.ModelForm):
    """
    Form for creating/editing Album instances.

    This is used by the HTML view, not the API.
    """
    class Meta:
        model = Album
        fields = ['title', 'format', 'artist_name', 'release_date', 'retail_price', 'cover_image']


class SongForm(forms.ModelForm):
    """
    Form for creating/editing Song instances.
    """
    class Meta:
        model = Song
        fields = ['title', 'album', 'length']


class PlaylistForm(forms.ModelForm):
    """
    Optional form for creating/editing playlists in the UI.

    Not all routes use this directly at the moment but it is useful
    if you extend the HTML views.
    """
    class Meta:
        model = Playlist
        fields = ['name', 'owner', 'songs', 'visibility']
