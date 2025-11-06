from django.contrib import admin
from .models import Album, Song, Playlist, DottifyUser, Comment, Rating


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist_name', 'format', 'release_date', 'retail_price')
    search_fields = ('title', 'artist_name')


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'length')
    search_fields = ('title',)
    list_filter = ('album',)


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'visibility', 'created_at')
    search_fields = ('name',)
    list_filter = ('visibility',)


@admin.register(DottifyUser)
class DottifyUserAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user')
    search_fields = ('display_name', 'user__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'text')
    search_fields = ('text', 'user__display_name', 'song__title')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'value')
    list_filter = ('value',)
    search_fields = ('user__display_name', 'song__title')
