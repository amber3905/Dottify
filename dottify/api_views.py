from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Album, Song, Playlist
from .serializers import AlbumSerializer, SongSerializer, PlaylistSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all().order_by('id')
    serializer_class = AlbumSerializer

    @action(detail=True, methods=['get'], url_path='songs')
    def songs(self, request, pk=None):
        album = self.get_object()
        songs = album.song_set.all()
        data = SongSerializer(songs, many=True, context={'request': request}).data
        return Response(data)

    @action(detail=True, methods=['get'], url_path=r'songs/(?P<song_pk>[^/.]+)')
    def song_detail(self, request, pk=None, song_pk=None):
        album = self.get_object()
        song = get_object_or_404(Song, pk=song_pk, album=album)
        data = SongSerializer(song, context={'request': request}).data
        return Response(data)


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all().order_by('id')
    serializer_class = SongSerializer


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all().order_by('id')
    serializer_class = PlaylistSerializer


@api_view(['GET'])
def statistics_view(request):
    data = {
        'album_count': Album.objects.count(),
        'song_count': Song.objects.count(),
        'playlist_count': Playlist.objects.count(),
    }
    return Response(data, status=status.HTTP_200_OK)
