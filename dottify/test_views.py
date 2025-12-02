from django.test import TestCase
from django.contrib.auth.models import User, Group
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
        cls.playlist.songs.add(cls.song)
        cls.artist_group, _ = Group.objects.get_or_create(name="Artist")
        cls.dottify_admin_group, _ = Group.objects.get_or_create(name="DottifyAdmin")
        cls.artist_user = User.objects.create_user(
            username="artist1",
            password="pw123",
            email="artist1@example.com",
        )
        cls.artist_duser = DottifyUser.objects.create(
            user=cls.artist_user,
            display_name="Artist One",
        )
        cls.artist_user.groups.add(cls.artist_group)
        cls.artist_album = Album.objects.create(
            title="Artist One Album",
            artist_name="Artist One",
        )
        cls.artist_song = Song.objects.create(
            title="Artist Song",
            album=cls.artist_album,
            length=200,
        )
        cls.other_artist_user = User.objects.create_user(
            username="artist2",
            password="pw123",
            email="artist2@example.com",
        )
        cls.other_artist_duser = DottifyUser.objects.create(
            user=cls.other_artist_user,
            display_name="Other Artist",
        )
        cls.other_artist_user.groups.add(cls.artist_group)
        cls.other_artist_album = Album.objects.create(
            title="Other Artist Album",
            artist_name="Other Artist",
        )
        cls.other_artist_song = Song.objects.create(
            title="Other Artist Song",
            album=cls.other_artist_album,
            length=210,
        )
        cls.admin_user = User.objects.create_user(
            username="adminuser",
            password="pw123",
            email="admin@example.com",
        )
        cls.admin_user.groups.add(cls.dottify_admin_group)

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
        self.user.groups.add(self.artist_group)
        self.client.login(username="alice", password="pw123")
        resp = self.client.get("/albums/new/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Album create page", resp.content.decode())

    def test_album_create_forbidden_for_non_artist(self):
        self.client.login(username="alice", password="pw123")
        resp = self.client.get("/albums/new/")
        self.assertEqual(resp.status_code, 403)

    def test_user_detail_redirects_to_lowercase(self):
        wrong_slug = "AnNiEmUsIcLoVeR92"
        resp = self.client.get(f"/users/{self.duser.id}/{wrong_slug}/")
        self.assertEqual(resp.status_code, 302)
        expected_path = f"/users/{self.duser.id}/{self.duser.display_name.lower()}/"
        self.assertIn(expected_path, resp["Location"])

    def test_user_detail_id_only_redirects_to_slug(self):
        resp = self.client.get(f"/users/{self.duser.id}/")
        self.assertEqual(resp.status_code, 302)
        expected_path = f"/users/{self.duser.id}/{self.duser.display_name.lower()}/"
        self.assertIn(expected_path, resp["Location"])

    def test_user_detail_slug_shows_playlists_and_songs(self):
        slug = self.duser.display_name.lower()
        resp = self.client.get(f"/users/{self.duser.id}/{slug}/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn(self.duser.display_name, html)
        self.assertIn(self.playlist.name, html)
        self.assertIn(self.song.title, html)

    def test_album_detail_by_id_is_public(self):
        resp = self.client.get(f"/albums/{self.album.id}/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn(self.album.title, html)
        self.assertIn("Test Song", html)

    def test_album_detail_with_slug_is_public_and_not_validated(self):
        wrong_slug = "this-is-wrong"
        resp = self.client.get(f"/albums/{self.album.id}/{wrong_slug}/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn(self.album.title, html)
        self.assertIn("Test Song", html)

    def test_album_delete_redirects_anonymous_to_login(self):
        resp = self.client.get(f"/albums/{self.artist_album.id}/delete/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Album.objects.filter(pk=self.artist_album.id).exists())

    def test_album_delete_forbidden_for_normal_user(self):
        self.client.login(username="alice", password="pw123")
        resp = self.client.get(f"/albums/{self.artist_album.id}/delete/")
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Album.objects.filter(pk=self.artist_album.id).exists())

    def test_album_delete_allowed_for_artist_owner(self):
        self.client.login(username="artist1", password="pw123")
        resp_get = self.client.get(f"/albums/{self.artist_album.id}/delete/")
        self.assertEqual(resp_get.status_code, 200)
        resp_post = self.client.post(f"/albums/{self.artist_album.id}/delete/")
        self.assertEqual(resp_post.status_code, 302)
        self.assertFalse(Album.objects.filter(pk=self.artist_album.id).exists())

    def test_album_delete_forbidden_for_non_owner_artist(self):
        self.client.login(username="artist1", password="pw123")
        resp_get = self.client.get(f"/albums/{self.other_artist_album.id}/delete/")
        self.assertEqual(resp_get.status_code, 403)
        resp_post = self.client.post(f"/albums/{self.other_artist_album.id}/delete/")
        self.assertEqual(resp_post.status_code, 403)
        self.assertTrue(Album.objects.filter(pk=self.other_artist_album.id).exists())

    def test_album_delete_allowed_for_dottifyadmin(self):
        self.client.login(username="adminuser", password="pw123")
        resp_get = self.client.get(f"/albums/{self.other_artist_album.id}/delete/")
        self.assertEqual(resp_get.status_code, 200)
        resp_post = self.client.post(f"/albums/{self.other_artist_album.id}/delete/")
        self.assertEqual(resp_post.status_code, 302)
        self.assertFalse(Album.objects.filter(pk=self.other_artist_album.id).exists())

    def test_song_create_forbidden_for_non_artist_or_admin(self):
        self.client.login(username="alice", password="pw123")
        resp_get = self.client.get("/songs/new/")
        self.assertEqual(resp_get.status_code, 403)
        resp_post = self.client.post("/songs/new/", {
            "title": "Non Artist Song",
            "album": self.artist_album.id,
            "length": 200,
        })
        self.assertEqual(resp_post.status_code, 403)
        self.assertFalse(Song.objects.filter(title="Non Artist Song").exists())

    def test_song_create_artist_can_create_on_own_album_only(self):
        self.client.login(username="artist1", password="pw123")
        resp_post_own = self.client.post("/songs/new/", {
            "title": "Artist Own Song",
            "album": self.artist_album.id,
            "length": 210,
        })
        self.assertEqual(resp_post_own.status_code, 302)
        self.assertTrue(
            Song.objects.filter(title="Artist Own Song", album=self.artist_album).exists()
        )
        resp_post_other = self.client.post("/songs/new/", {
            "title": "Should Not Be Created",
            "album": self.other_artist_album.id,
            "length": 220,
        })
        self.assertEqual(resp_post_other.status_code, 403)
        self.assertFalse(Song.objects.filter(title="Should Not Be Created").exists())

    def test_song_create_admin_sees_form_and_can_create_on_any_album(self):
        self.client.login(username="adminuser", password="pw123")
        resp_get = self.client.get("/songs/new/")
        self.assertEqual(resp_get.status_code, 200)
        resp_post = self.client.post("/songs/new/", {
            "title": "Admin Created Song",
            "album": self.other_artist_album.id,
            "length": 230,
        })
        self.assertEqual(resp_post.status_code, 302)
        self.assertTrue(
            Song.objects.filter(title="Admin Created Song", album=self.other_artist_album).exists()
        )

    def test_song_edit_redirects_anonymous_to_login(self):
        resp = self.client.get(f"/songs/{self.artist_song.id}/edit/")
        self.assertEqual(resp.status_code, 302)

    def test_song_edit_forbidden_for_normal_user(self):
        self.client.login(username="alice", password="pw123")
        resp = self.client.get(f"/songs/{self.artist_song.id}/edit/")
        self.assertEqual(resp.status_code, 403)

    def test_song_edit_allowed_for_artist_owner(self):
        self.client.login(username="artist1", password="pw123")
        resp_get = self.client.get(f"/songs/{self.artist_song.id}/edit/")
        self.assertEqual(resp_get.status_code, 200)
        resp_post = self.client.post(f"/songs/{self.artist_song.id}/edit/", {
            "title": "Updated Artist Song",
            "album": self.artist_album.id,
            "length": 222,
        })
        self.assertEqual(resp_post.status_code, 302)
        self.assertTrue(
            Song.objects.filter(pk=self.artist_song.id, title="Updated Artist Song").exists()
        )

    def test_song_edit_forbidden_for_non_owner_artist(self):
        self.client.login(username="artist1", password="pw123")
        resp_get = self.client.get(f"/songs/{self.other_artist_song.id}/edit/")
        self.assertEqual(resp_get.status_code, 403)
        resp_post = self.client.post(f"/songs/{self.other_artist_song.id}/edit/", {
            "title": "Should Not Change",
            "album": self.other_artist_album.id,
            "length": 300,
        })
        self.assertEqual(resp_post.status_code, 403)
        self.assertFalse(
            Song.objects.filter(pk=self.other_artist_song.id, title="Should Not Change").exists()
        )

    def test_song_edit_allowed_for_dottifyadmin(self):
        self.client.login(username="adminuser", password="pw123")
        resp_get = self.client.get(f"/songs/{self.other_artist_song.id}/edit/")
        self.assertEqual(resp_get.status_code, 200)
        resp_post = self.client.post(f"/songs/{self.other_artist_song.id}/edit/", {
            "title": "Admin Edited Song",
            "album": self.other_artist_album.id,
            "length": 333,
        })
        self.assertEqual(resp_post.status_code, 302)
        self.assertTrue(
            Song.objects.filter(pk=self.other_artist_song.id, title="Admin Edited Song").exists()
        )

    def test_song_delete_redirects_anonymous_to_login(self):
        resp = self.client.get(f"/songs/{self.artist_song.id}/delete/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Song.objects.filter(pk=self.artist_song.id).exists())

    def test_song_delete_forbidden_for_normal_user(self):
        self.client.login(username="alice", password="pw123")
        resp = self.client.get(f"/songs/{self.artist_song.id}/delete/")
        self.assertEqual(resp.status_code, 403)
        resp_post = self.client.post(f"/songs/{self.artist_song.id}/delete/")
        self.assertEqual(resp_post.status_code, 403)
        self.assertTrue(Song.objects.filter(pk=self.artist_song.id).exists())

    def test_song_delete_allowed_for_artist_owner(self):
        self.client.login(username="artist1", password="pw123")
        resp_get = self.client.get(f"/songs/{self.artist_song.id}/delete/")
        self.assertEqual(resp_get.status_code, 200)
        resp_post = self.client.post(f"/songs/{self.artist_song.id}/delete/")
        self.assertEqual(resp_post.status_code, 302)
        self.assertFalse(Song.objects.filter(pk=self.artist_song.id).exists())

    def test_song_delete_forbidden_for_non_owner_artist(self):
        self.client.login(username="artist1", password="pw123")
        resp_get = self.client.get(f"/songs/{self.other_artist_song.id}/delete/")
        self.assertEqual(resp_get.status_code, 403)
        resp_post = self.client.post(f"/songs/{self.other_artist_song.id}/delete/")
        self.assertEqual(resp_post.status_code, 403)
        self.assertTrue(Song.objects.filter(pk=self.other_artist_song.id).exists())

    def test_song_delete_allowed_for_dottifyadmin(self):
        self.client.login(username="adminuser", password="pw123")
        resp_get = self.client.get(f"/songs/{self.other_artist_song.id}/delete/")
        self.assertEqual(resp_get.status_code, 200)
        resp_post = self.client.post(f"/songs/{self.other_artist_song.id}/delete/")
        self.assertEqual(resp_post.status_code, 302)
        self.assertFalse(Song.objects.filter(pk=self.other_artist_song.id).exists())