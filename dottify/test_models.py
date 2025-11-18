from django.test import TestCase
from django.contrib.auth.models import User
from dottify.models import (
    Album,
    Song,
    Playlist,
    DottifyUser,
)


class DottifyModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('u1', password='pw')
        self.duser = DottifyUser.objects.create(user=self.user, display_name='MyDisplay')
        self.album = Album.objects.create(
            title='Test Album',
            artist_name='Some Artist',
        )
        self.song1 = Song.objects.create(title='Song 1', album=self.album, length=180)
        self.song2 = Song.objects.create(title='Song 2', album=self.album, length=200)

    def test_album_str(self):
        self.assertEqual(str(self.album), 'Test Album - Some Artist')

    def test_song_str(self):
        self.assertEqual(str(self.song1), 'Song 1')

    def test_playlist_m2m_songs(self):
        pl = Playlist.objects.create(name='Gym Mix', owner=self.duser, visibility=2)
        pl.songs.add(self.song1, self.song2)
        self.assertEqual(pl.songs.count(), 2)
        self.assertIn(pl, self.song1.playlists.all())

    def test_dottify_user_str(self):
        self.assertEqual(str(self.duser), 'MyDisplay')

    def test_album_allows_null_price(self):
        self.assertIsNone(self.album.retail_price)
