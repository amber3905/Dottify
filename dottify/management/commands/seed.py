import csv
import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from dottify.models import Album, Song


class Command(BaseCommand):
    help = "Seed the database with sample albums, songs, and cover images from CSV files."

    def handle(self, *args, **options):
        # data directory: dottify/management/data/
        data_dir = os.path.join(settings.BASE_DIR, "dottify", "management", "data")
        albums_csv = os.path.join(data_dir, "albums.csv")
        songs_csv = os.path.join(data_dir, "songs.csv")
        images_dir = os.path.join(data_dir, "images")

        if not os.path.exists(albums_csv):
            self.stdout.write(self.style.ERROR(f"albums.csv not found in {data_dir}"))
            return

        # make sure media/albums/ exists
        media_albums_dir = os.path.join(settings.MEDIA_ROOT, "albums")
        os.makedirs(media_albums_dir, exist_ok=True)

        # ------------------------------------------------------------------
        # 1) LOAD ALBUMS  (ID, Artist, Album, Released, Price, Format)
        # ------------------------------------------------------------------
        self.stdout.write("Loading albums...")
        id_to_album = {}  # so we can attach songs later by numeric ID

        with open(albums_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                album_id = row.get("ID")
                title = row.get("Album")
                artist = row.get("Artist") or "Unknown"
                released = row.get("Released") or None
                price = row.get("Price") or None
                fmt = row.get("Format") or "ALB"

                if not title:
                    self.stdout.write(self.style.WARNING(f"Skipping row {i}: no Album name"))
                    continue

                album_obj, created = Album.objects.get_or_create(
                    title=title,
                    artist_name=artist,
                    defaults={
                        "release_date": released,
                        "retail_price": price,
                        "format": fmt,
                    },
                )

                # try to match an image: slug of title + startswith
                if os.path.isdir(images_dir):
                    wanted_slug = slugify(title)
                    # look for any file in images_dir that starts with that slug
                    for fname in os.listdir(images_dir):
                        if fname.startswith(wanted_slug):
                            src_img = os.path.join(images_dir, fname)
                            dest_img = os.path.join(media_albums_dir, fname)
                            shutil.copyfile(src_img, dest_img)
                            album_obj.cover_image = f"albums/{fname}"
                            album_obj.save()
                            break  # stop at first match

                if album_id:
                    id_to_album[album_id] = album_obj

        self.stdout.write(self.style.SUCCESS("✅ Albums loaded."))

        # ------------------------------------------------------------------
        # 2) LOAD SONGS  (Album, Song, Duration)
        # ------------------------------------------------------------------
        if not os.path.exists(songs_csv):
            self.stdout.write(self.style.WARNING("songs.csv not found, skipping songs."))
            return

        self.stdout.write("Loading songs...")
        with open(songs_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                album_ref = row.get("Album")      # in your file this is the numeric ID
                title = row.get("Song")
                duration = row.get("Duration") or "0"

                if not title:
                    self.stdout.write(self.style.WARNING(f"Skipping song row {i}: no Song name"))
                    continue

                # your songs.csv uses the album's ID (e.g. "1") not the name
                album_obj = id_to_album.get(str(album_ref))
                if not album_obj:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping song '{title}': album ID {album_ref} not found")
                    )
                    continue

                try:
                    length = int(duration)
                except ValueError:
                    length = 0

                Song.objects.get_or_create(
                    title=title,
                    album=album_obj,
                    defaults={"length": length},
                )

        self.stdout.write(self.style.SUCCESS("✅ Songs loaded."))
        self.stdout.write(self.style.SUCCESS("🎵 Seeding complete."))
