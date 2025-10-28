# Write your URL patterns here.
from django.contrib import admin
from django.urls import path, include
from rest_framework_nested import routers
from dottify.api_views import (
    DottifyUserViewSet, AlbumViewSet, SongViewSet,
    PlaylistViewSet, RatingViewSet, CommentViewSet
)

router = routers.DefaultRouter()
router.register(r'users', DottifyUserViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'playlists', PlaylistViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'comments', CommentViewSet)

album_router = routers.NestedSimpleRouter(router, r'albums', lookup = 'album')
album_router.register(r'songs', SongViewSet, basename = 'song')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(album_router.urls)),
]
