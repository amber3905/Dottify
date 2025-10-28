# Seeding carries no marks but may help you test your work.
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from dottify.models import (
    DottifyUser, Album, Song, Playlist, Rating, Comment
)

class Command(BaseCommand):
    help = 'Insert sample data into database for user testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        user, _ = User.objects.get_or_create(username='amber', defaults={'email': 'amber@example.com'})
        user.set_password('12345')
        user.save()
        dottify_user, _ = DottifyUser.objects.get_or_create(user=user, display_name="Amber Waves")

        album1, _ = Album.objects.get_or_create(
            title="Midnight Echoes",
            artist_name="Amber Waves",
            artist_account=dottify_user,
            retail_price=9.99,
            format="SNGL",
            release_date=date.today() - timedelta(days=7)
        )
        album2, _ = Album.objects.get_or_create(
            title="Electric Skies",
            artist_name="Amber Waves",
            artist_account=dottify_user,
            retail_price=11.49,
            format="DLUX",
            release_date=date.today()
        )

        song1, _ = Song.objects.get_or_create(title="Dreamlight", length=180, album=album1)
        song2, _ = Song.objects.get_or_create(title="Neon Drift", length=200, album=album1)
        song3, _ = Song.objects.get_or_create(title="Voltage", length=220, album=album2)

        playlist, _ = Playlist.objects.get_or_create(
            name="Chill Vibes",
            owner=dottify_user,
            visibility=2
        )
        playlist.songs.set([song1, song2])
        playlist.save()

        Rating.objects.get_or_create(stars=4.5)
        Rating.objects.get_or_create(stars=3.0)

        Comment.objects.get_or_create(comment_text="Amazing album!")
        Comment.objects.get_or_create(comment_text="Love the vibe")

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
        self.stdout.write("You can now test API endpoints such as:")
        self.stdout.write("  - /api/users/")
        self.stdout.write("  - /api/albums/")
        self.stdout.write("  - /api/albums/1/songs/")
        self.stdout.write("  - /api/playlists/")
        self.stdout.write("  - /api/comments/")