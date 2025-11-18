from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.static import serve
from django.conf import settings

from .api_views import AlbumViewSet, SongViewSet, PlaylistViewSet, statistics_view
from . import views

# Single router for all REST API endpoints within this sub-app.
router = DefaultRouter()
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'songs', SongViewSet, basename='song')
router.register(r'playlists', PlaylistViewSet, basename='playlist')

urlpatterns = [
    # --- API routes ---
    path('api/', include(router.urls)),
    path('api/statistics/', statistics_view, name='api-statistics'),

    # --- HTML views ---
    path('', views.index, name='index'),

    # Album routes
    path('albums/', views.album_list, name='album-list')
    ,
    path('albums/new/', views.album_create, name='album-create'),
    path('albums/search/', views.album_search, name='album-search'),
    path('albums/<int:album_id>/', views.album_detail_by_id, name='album-detail-id'),
    path('albums/<int:album_id>/<slug:slug>/', views.album_detail_with_slug, name='album-detail-slug'),
    path('albums/<int:album_id>/edit/', views.album_edit, name='album-edit'),
    path('albums/<int:album_id>/delete/', views.album_delete, name='album-delete'),

    # Song routes
    path('songs/', views.song_list, name='song-list'),
    path('songs/new/', views.song_new, name='song-new'),
    path('songs/<int:song_id>/', views.song_detail, name='song-detail'),
    path('songs/<int:song_id>/edit/', views.song_edit, name='song-edit'),
    path('songs/<int:song_id>/delete/', views.song_delete, name='song-delete'),

    # Playlist routes
    path('playlists/', views.playlist_list, name='playlist-list'),
    path('playlists/<int:playlist_id>/', views.playlist_detail, name='playlist-detail'),

    # User profile routes
    path('users/<int:user_id>/', views.user_detail_redirect, name='user-detail'),
    path('users/<int:user_id>/<slug:slug>/', views.user_detail_slug, name='user-detail-slug'),

    # Help / support route
    path('help/', views.help_view, name='help'),

    # Media helper for serving uploaded files during development.
    # Note: ROOT_URLCONF must not be changed; this lives entirely in
    # the dottify sub-app and is safe for the coursework.
    path(
        'app-media/<path:path>/',
        serve,
        {'document_root': settings.MEDIA_ROOT},
        name='app-media',
    ),
]
