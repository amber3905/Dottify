from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

def default_cover():
    """
    Default value for Album.cover_image.

    We return an empty string rather than None so that the ImageField
    always has a string path. This keeps the field optional without
    forcing a real file to exist.
    """
    return ''

class DottifyUser(models.Model):
    """
    Profile model that extends Django's built-in User.

    Sheet C/D talk about 'display names' for playlists and comments.
    We keep authentication on auth.User, but expose display_name here.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150)
    def __str__(self):
        return self.display_name

class Album(models.Model):
    """
    Represents a single album / EP / single in the catalogue.
    """
    FORMAT_SNGL = "SNGL"
    FORMAT_RMST = "RMST"
    FORMAT_DLUX = "DLUX"
    FORMAT_COMP = "COMP"
    FORMAT_LIVE = "LIVE"
    FORMAT_CHOICES = [
        (FORMAT_SNGL, "Single"),
        (FORMAT_RMST, "Remaster"),
        (FORMAT_DLUX, "Deluxe Edition"),
        (FORMAT_COMP, "Compilation"),
        (FORMAT_LIVE, "Live Recording"),
    ]
    title = models.CharField(max_length=200)
    format = models.CharField(
        max_length=8,
        choices=FORMAT_CHOICES,
        null=True,
        blank=True,
    )
    artist_name = models.CharField(max_length=200)
    release_date = models.DateField(null=True, blank=True)
    retail_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True,
    )
    cover_image = models.ImageField(upload_to='', null=True, blank=True, default=default_cover)
    def __str__(self):
        return f"{self.title} - {self.artist_name}"

class Song(models.Model):
    """
    A song belongs to exactly one Album.
    """
    title = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    length = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title

class Playlist(models.Model):
    """
    User-owned collections of songs.
    Visibility matches the stakeholder's three states:
    - 0 = Private
    - 1 = Unlisted
    - 2 = Public
    """
    VISIBILITY = [
        (0, 'Private'),
        (1, 'Unlisted'),
        (2, 'Public'),
    ]
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        DottifyUser,
        on_delete=models.CASCADE,
        related_name='playlist_set',
    )
    songs = models.ManyToManyField(
        Song,
        blank=True,
        related_name='playlists',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    visibility = models.IntegerField(choices=VISIBILITY, default=2)
    def __str__(self):
        return self.name

class Comment(models.Model):
    """
    Read-only comments for playlists (Sheet D requirement).
    playlist is used in the UI; song is available for future extension.
    Users are linked through DottifyUser so we can show display_name.
    """
    user = models.ForeignKey(DottifyUser, on_delete=models.CASCADE, null=True, blank=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, blank=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(blank=True)

class Rating(models.Model):
    """
    Read-only ratings for albums/songs (Sheet D requirement).
    Album ratings are aggregated on the album detail view to show
    lifetime and recent averages.
    """
    user = models.ForeignKey(DottifyUser, on_delete=models.CASCADE, null=True, blank=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    value = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)