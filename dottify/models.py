from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


def default_cover():
    return ''


class DottifyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150)

    def __str__(self):
        return self.display_name


class Album(models.Model):
    FORMAT_CHOICES = [
        ('ALB', 'Album'),
        ('SNGL', 'Single'),
        ('EP', 'EP'),
    ]
    title = models.CharField(max_length=200)
    format = models.CharField(max_length=8, choices=FORMAT_CHOICES, default='ALB')
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
    title = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    length = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Playlist(models.Model):
    VISIBILITY = [
        (0, 'Private'),
        (1, 'Unlisted'),
        (2, 'Public'),
    ]
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(DottifyUser, on_delete=models.CASCADE, related_name='playlist_set')
    songs = models.ManyToManyField(Song, blank=True, related_name='playlists')
    created_at = models.DateTimeField(auto_now_add=True)
    visibility = models.IntegerField(choices=VISIBILITY, default=2)

    def __str__(self):
        return self.name


class Comment(models.Model):
    user = models.ForeignKey(DottifyUser, on_delete=models.CASCADE, null=True, blank=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, blank=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(blank=True)


class Rating(models.Model):
    user = models.ForeignKey(DottifyUser, on_delete=models.CASCADE, null=True, blank=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    value = models.IntegerField(null=True, blank=True)
