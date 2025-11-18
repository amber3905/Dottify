from rest_framework import serializers
from .models import Album, Song, Playlist, DottifyUser


class SongSerializer(serializers.ModelSerializer):
    """
    Serialiser for Song objects, used both directly and nested
    inside AlbumSerializer.
    """
    class Meta:
        model = Song
        fields = ['id', 'title', 'length', 'album']


class AlbumSerializer(serializers.ModelSerializer):
    """
    Album serialiser including nested songs.

    The song_set field is read-only and mirrors the reverse relation
    Album -> Song defined by the ForeignKey on Song.
    """
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
    """
    Serialiser for playlists.

    - owner is a foreign key to DottifyUser (not auth.User) so we can
      expose display names if needed elsewhere.
    - songs is a list of Song IDs (writeable).
    """
    owner = serializers.PrimaryKeyRelatedField(queryset=DottifyUser.objects.all())
    songs = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Playlist
        fields = ['id', 'songs', 'owner', 'name', 'created_at', 'visibility']


class DottifyUserSerializer(serializers.ModelSerializer):
    """
    Minimal serialiser for DottifyUser.

    Exposes the underlying auth.User primary key plus the display name.
    """
    class Meta:
        model = DottifyUser
        fields = ['id', 'user', 'display_name']
