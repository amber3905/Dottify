from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from dottify.models import (
    DottifyUser, Album, Song, Playlist, Rating, Comment
)
from datetime import date

class BaseAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username = 'amber', password = '12345')
        self.dottify_user = DottifyUser.objects.create(user = self.user, display_name = "Amber")

        self.album = Album.objects.create(
            title = "Midnight Echoes",
            artist_name = "Amber Waves",
            artist_account = self.dottify_user,
            retail_price = '9.99',
            format = "SNGL",
            release_date = date.today(),
        )

        self.song = Song.objects.create(title = "Dreamlight", length = 180, album = self.album)

        self.playlist = Playlist.objects.create(name = "Chill Vibes", owner = self.dottify_user)
        self.playlist.songs.add(self.song)

        self.rating = Rating.objects.create(stars = 4.5)
        self.comment = Comment.objects.create(comment_text = "Nice album!")

class DottifyUserAPITests(BaseAPITestCase):
    def test_list_users(self):
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["display_name"], "Amber")

class AlbumAPITests(BaseAPITestCase):
    def test_list_albums(self):
        response = self.client.get("/api/albums/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "Midnight Echoes")

    def test_create_album(self):
        payload = {
            "title": "New Horizons",
            "artist_name": "Amber Waves",
            "artist_account": self.dottify_user.id,
            "retail_price": "12.50",
            "format": "DLUX",
            "release_date": str(date.today()),
        }
        response = self.client.post("/api/albums/", payload, format = "json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class SongAPITests(BaseAPITestCase):
    def test_list_songs_under_album(self):
        url = f"/api/albums/{self.album.id}/songs/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "Dreamlight")

    def test_create_song_under_album(self):
        url = f"/api/albums/{self.album.id}/songs/"
        payload = {"title": "Aurora", "length": 220, "album": self.album.id}
        response = self.client.post(url, payload, format = "json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Song.objects.filter(title = "Aurora").exists())

class PlaylistAPITests(BaseAPITestCase):
    def test_list_playlists(self):
        response = self.client.get("/api/playlists/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Chill Vibes")

    def test_create_playlist(self):
        payload = {
            "name": "Workout",
            "songs": [self.song.id],
            "visibility": 2,
            "owner": self.dottify_user.id,
        }
        response = self.client.post("/api/playlists/", payload, format = "json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class RatingAPITests(BaseAPITestCase):
    def test_create_rating(self):
        payload = {"stars": 3.5}
        response = self.client.post("/api/ratings/", payload, format = "json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Rating.objects.filter(stars = 3.5).exists())

class CommentAPITests(BaseAPITestCase):
    def test_create_comment(self):
        payload = {"comment_text": "Loved it!"}
        response = self.client.post("/api/comments/", payload, format = "json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(comment_text = "Loved it!").exists())