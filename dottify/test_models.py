from django.test import TestCase
from django.contrib.auth.models import User
from .models import Album, Song, DottifyUser

class DottifyModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.dottify_user = DottifyUser.objects.create(
            user=self.user, display_name='Test Artist'
        )
        self.album = Album.objects.create(
            title='Test Album',
            artist_name='Test Artist',
            retail_price=5.99,
            release_date='2025-01-01'
        )

    def test_album_str_returns_title_and_artist(self):
        self.assertEqual(str(self.album), "Test Album by Test Artist")

    def test_song_position_auto_increments(self):
        song1 = Song.objects.create(title='Song 1', length=200, album=self.album)
        song2 = Song.objects.create(title='Song 2', length=210, album=self.album)
        self.assertEqual(song1.position, 1)
        self.assertEqual(song2.position, 2)

    def test_dottify_user_str(self):
        self.assertEqual(str(self.dottify_user), 'Test Artist')