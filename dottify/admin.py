from django.contrib import admin
from .models import(
    DottifyUser,
    Album,
    Song,
    Playlist,
    Rating,
    Comment
)

# Register your models here.
@admin.register(DottifyUser)
class DottifyUserAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user')
    search_fields = ('display_name', 'user__username')

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist_name', 'format', 'retail_price', 'release_date')
    list_filter = ('format', 'release_date')
    search_fields = ('title', 'artist_name')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'position', 'length')
    list_filter = ('album',)
    search_fields = ('title',)
    readonly_fields = ('position',)

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'visibility', 'created_at')
    list_filter = ('visibility', 'created_at')
    search_fields = ('name', 'owner__display_name')
    filter_horizontal = ('songs',)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('stars',)
    list_filter = ('stars',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_text',)
    search_fields = ('comment_text',)