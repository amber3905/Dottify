from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from dottify.models import Album, Song, DottifyUser, Playlist


class DottifyAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.album = Album.objects.create(
            title='API Album',
            artist_name='API Artist',
            format='ALB',
        )
        self.song = Song.objects.create(title='API Song', album=self.album, length=123)

        user = User.objects.create_user('owner', password='pw')
        self.duser = DottifyUser.objects.create(user=user, display_name='OwnerDisplay')
        self.playlist = Playlist.objects.create(name='API Playlist', owner=self.duser)

    def test_album_list_includes_song_set(self):
        resp = self.client.get('/api/albums/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertIn('song_set', data[0])

    def test_nested_album_songs_endpoint(self):
        resp = self.client.get(f'/api/albums/{self.album.id}/songs/')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['title'], 'API Song')

    def test_statistics_endpoint(self):
        resp = self.client.get('/api/statistics/')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        for key in ['album_count', 'song_count', 'playlist_count']:
            self.assertIn(key, body)
