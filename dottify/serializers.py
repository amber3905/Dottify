from rest_framework import serializers
from .models import Album, Song, Playlist, DottifyUser


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'title', 'length', 'album']


class AlbumSerializer(serializers.ModelSerializer):
    song_set = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = [
            'id',
            'cover_image',
            'title',
            'artist_name',
            'retail_price',
            'format',
            'release_date',
            'song_set',
        ]


class PlaylistSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=DottifyUser.objects.all())
    songs = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(), many=True, required=False)

    class Meta:
        model = Playlist
        fields = ['id', 'songs', 'owner', 'name', 'created_at', 'visibility']


class DottifyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DottifyUser
        fields = ['id', 'user', 'display_name']
