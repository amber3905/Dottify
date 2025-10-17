from django.db import models
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta

# Create your models here.
class DottifyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=800)

    def __str__(self):
        return self.display_name

class AlbumFormat(models.TextChoices):
    SINGLE = 'SNGL', _('Single')
    REMASTER = 'RMST', _('Remaster')
    DELUXE = 'DLUX', _('Deluxe Edition')
    COMPILATION = 'COMP', _('Compilation')
    LIVE = 'LIVE', _('Live Recording')

def default_cover():
    return "default_cover.jpg"

class Album(models.Model):
    title = models.CharField(max_length=800)
    artist_name = models.CharField(max_length=800)
    artist_account = models.ForeignKey(DottifyUser, null=True, blank=True, on_delete=models.SET_NULL)
    retail_price = models.DecimalField(max_digits=5, decimal_places=2,
                                       validators=[MinValueValidator(0), MaxValueValidator(999.999)])
    format = models.CharField(max_length=4, choices=AlbumFormat.choices, null=True, blank=True)
    release_date = models.DateField()
    cover_image = models.ImageField(blank=True, null=True, default=default_cover)
    slug = models.SlugField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'artist_name', 'format'],
                                    name='unique_album_per_artist_format')
        ]
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        if self.release_date > date.today() + timedelta(days=183):
            raise ValidationError("Release date cannot be more than 6 months in the future.")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} by {self.artist_name}"

class Song(models.Model):
    title = models.CharField(max_length=800)
    running_time = models.PositiveIntegerField(validators=[MinValueValidator(10)])
    position = models.PositiveIntegerField(null=True, editable=False)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'album'], name='unique_song_per_album')
        ]
        ordering = ['position']
    
    def save(self, *args, **kwargs):
        if self._state.adding and self.position is None:
            last_pos = Song.objects.filter(album=self.album).count()
            self.position = last_pos + 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.album.title})"

class VisibilityLevel(models.IntegerChoices):
    HIDDEN = 0, _('Hidden')
    UNLISTED = 1, _('Unlisted')
    PUBLIC = 2, _('Public')

class Playlist(models.Model):
    name = models.CharField(max_length=800)
    created_at = models.DateTimeField(auto_now_add=True)
    songs = models.ManyToManyField(Song)
    visibility = models.IntegerField(choices=VisibilityLevel.choices, default=0)
    owner = models.ForeignKey(DottifyUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.get_visibility_display()})"
    
class Rating(models.Model):
    stars = models.DecimalField(max_digits=2, decimal_places=1,
                                validators=[MinValueValidator(0), MaxValueValidator(5)])

    def save(self, *args, **kwargs):
        if (self.stars * 10) % 5 != 0:
            raise ValidationError("Stars must be in increments of 0.5.")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.stars} *"

class Comment(models.Model):
    comment_text = models.CharField(max_length=800)

    def __str__(self):
        return self.comment_text[:50]