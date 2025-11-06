from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from dottify.models import (
    DottifyUser,
    Playlist,
    Comment,
    Album,
    Rating,
    Song,
)


class SheetDTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create a real Django user (for login + help view)
        cls.auth_user = User.objects.create_user(
            username="sheetduser",
            password="pw123",
            email="sheetd@example.com",
        )
        # link to DottifyUser
        cls.duser = DottifyUser.objects.create(
            user=cls.auth_user,
            display_name="SheetDUser",
        )

        # playlist + comment
        cls.playlist = Playlist.objects.create(
            name="My Chill Playlist",
            owner=cls.duser,
        )
        cls.comment = Comment.objects.create(
            user=cls.duser,
            playlist=cls.playlist,
            text="This is a great playlist!",
        )

        # album + ratings
        cls.album = Album.objects.create(
            title="Rated Album",
            artist_name="Test Artist",
        )
        Rating.objects.create(user=cls.duser, album=cls.album, value=4)
        Rating.objects.create(user=cls.duser, album=cls.album, value=2)

        # songs (for list count + album detail)
        cls.song1 = Song.objects.create(
            title="Song One",
            album=cls.album,
            length=120,
        )
        cls.song2 = Song.objects.create(
            title="Song Two",
            album=cls.album,
            length=150,
        )

    # -------------------------------------------------------------
    # PLAYLIST TESTS
    # -------------------------------------------------------------
    def test_playlist_list_view_exists(self):
        """
        /playlists/ should return 200 and list playlist names.
        """
        resp = self.client.get("/playlists/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("My Chill Playlist", html)

    def test_playlist_detail_shows_comments(self):
        """
        /playlists/<id>/ should show the comment text AND the display name
        of the user who made it (Sheet D requirement).
        """
        resp = self.client.get(f"/playlists/{self.playlist.id}/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("My Chill Playlist", html)
        self.assertIn("This is a great playlist!", html)
        self.assertIn("SheetDUser", html)

    # -------------------------------------------------------------
    # SONG LIST TEST
    # -------------------------------------------------------------
    def test_song_list_shows_total_results(self):
        """
        Sheet D: song list page must show 'Total results found: N'
        """
        resp = self.client.get("/songs/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        # we created 2 songs in setUpTestData
        self.assertIn("Total results found: 2", html)

    # -------------------------------------------------------------
    # ALBUM DETAIL / RATINGS TEST
    # -------------------------------------------------------------
    def test_album_detail_shows_rating_lines(self):
        """
        Sheet D: album detail should show both rating lines
        ('Average rating of all time' and 'Recent rating average ...')
        """
        resp = self.client.get(f"/albums/{self.album.id}/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("Average rating of all time:", html)
        self.assertIn("Recent rating average (last 7 days):", html)

    # -------------------------------------------------------------
    # HELP VIEW (Lab 5 style) – requires login
    # -------------------------------------------------------------
    def test_help_view_requires_login_and_renders(self):
        """
        Our help view is @login_required, so:
        - anonymous users get redirected
        - logged-in users see the form
        """
        # anonymous first
        resp = self.client.get("/help/")
        self.assertNotEqual(resp.status_code, 200)  # likely 302 to /accounts/login/

        # now login
        self.client.login(username="sheetduser", password="pw123")
        resp2 = self.client.get("/help/")
        self.assertEqual(resp2.status_code, 200)
        self.assertIn("Contact Support", resp2.content.decode())
