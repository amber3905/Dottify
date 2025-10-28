# Use this file for your API viewsets only
# E.g., from rest_framework import ...
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import (
    DottifyUser, Album, Song, Playlist, Rating, Comment
)
from .serializers import (
    DottifyUserSerializer, AlbumSerializer, SongSerializer,
    PlaylistSerializer, RatingSerializer, CommentSerializer
)

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

class DottifyUserViewSet(BaseViewSet):
    queryset = DottifyUser.objects.select_related('user').all()
    serializer_class = DottifyUserSerializer

class AlbumViewSet(BaseViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

class SongViewSet(BaseViewSet):
    serializer_class = SongSerializer
    def get_queryset(self):
        album_pk = self.kwargs.get('album_pk')
        if album_pk:
            return Song.objects.filter(album_id = album_pk)
        return Song.objects.all()

class PlaylistViewSet(BaseViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

class RatingViewSet(BaseViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class CommentViewSet(BaseViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer