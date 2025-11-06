from django.test import TestCase
from django.contrib.auth.models import User
from dottify.models import Album, DottifyUser, Playlist


class DottifyViewTests(TestCase):
    def setUp(self):
        # your app creates 'alice' via post_migrate, so in tests we just fetch it
        self.user, _ = User.objects.get_or_create(
            username='alice',
            defaults={'email': 'alice@example.com'}
        )
        # ensure password is correct for login
        self.user.set_password('pw123')
        self.user.save()

        self.duser = DottifyUser.objects.create(user=self.user, display_name='AnnieMusicLover92')

        self.album = Album.objects.create(title='Greatest Hits', artist_name='Various')
        self.playlist = Playlist.objects.create(name='Work Jams 2', owner=self.duser)

    def test_index_shows_albums_and_playlists(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        text = resp.content.decode()
        self.assertIn('Greatest Hits', text)
        self.assertIn('Work Jams 2', text)

    def test_album_create_route_exists(self):
        resp = self.client.get('/albums/new/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Album create page', resp.content.decode())

    def test_album_search_requires_login(self):
        resp = self.client.get('/albums/search/?q=Greatest')
        self.assertEqual(resp.status_code, 401)

    def test_album_search_allows_logged_in(self):
        logged_in = self.client.login(username='alice', password='pw123')
        self.assertTrue(logged_in, "Login with alice/pw123 should succeed")
        resp = self.client.get('/albums/search/?q=Greatest')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Greatest Hits', resp.content.decode())

    def test_user_detail_redirects_to_lowercase(self):
        resp = self.client.get(f'/users/{self.duser.id}/')
        self.assertEqual(resp.status_code, 302)
        # display name is AnnieMusicLover92 -> lower() in view
        self.assertIn('/users/1/anniemusiclover92/', resp.url)
