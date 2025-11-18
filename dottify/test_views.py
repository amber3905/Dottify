from django.test import TestCase
from django.contrib.auth.models import User

from dottify.models import Album, Song, Playlist, DottifyUser


class DottifyViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="alice",
            password="pw123",
            email="alice@example.com",
        )
        cls.duser = DottifyUser.objects.create(
            user=cls.user,
            display_name="AnnieMusicLover92",
        )
        cls.album = Album.objects.create(
            title="Test Album",
            artist_name="Test Artist",
        )
        cls.song = Song.objects.create(
            title="Test Song",
            album=cls.album,
            length=180,
        )
        cls.playlist = Playlist.objects.create(
            name="My Playlist",
            owner=cls.duser,
        )

    def test_index_shows_albums_and_playlists(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("Test Album", html)
        self.assertIn("My Playlist", html)

    def test_album_search_requires_login(self):
        resp = self.client.get("/albums/search/?q=Test")
        self.assertEqual(resp.status_code, 401)

    def test_album_search_allows_logged_in(self):
        self.client.login(username="alice", password="pw123")
        resp = self.client.get("/albums/search/?q=Test")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Test Album", resp.content.decode())

    def test_album_create_route_exists(self):
        self.client.login(username="alice", password="pw123")
        resp = self.client.get("/albums/new/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Album create page", resp.content.decode())

    def test_user_detail_redirects_to_lowercase(self):
        wrong_slug = "AnNiEmUsIcLoVeR92"
        resp = self.client.get(f"/users/{self.duser.id}/{wrong_slug}/")
        self.assertEqual(resp.status_code, 302)
        expected_path = f"/users/{self.duser.id}/{self.duser.display_name.lower()}/"
        self.assertIn(expected_path, resp["Location"])
