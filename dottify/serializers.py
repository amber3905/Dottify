# Write your API serialisers here.
from rest_framework import serializers
from .models import (
    DottifyUser, Album, Song, Playlist, Rating, Comment
)

class DottifyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DottifyUser
        fields = ['id', 'display_name', 'user']

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'title', 'length', 'position', 'album']
        read_only_fields = ['position']

class AlbumSerializer(serializers.ModelSerializer):
    songs = serializers.StringRelatedField(many = True, read_only = True)
    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist_name', 'artist_account',
            'retail_price', 'format', 'release_date',
            'cover_image', 'slug', 'songs'
        ]
        read_only_fields = ['slug']

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'created_at', 'songs', 'visibility', 'owner']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'stars']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'comment_text']