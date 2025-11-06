from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django import forms
from .models import Album, Song, Playlist, DottifyUser, Comment, Rating
from .forms import AlbumForm, SongForm


# ---------------- HOME ----------------
def index(request):
    playlists = Playlist.objects.all()
    albums = Album.objects.all()
    context = {'playlists': playlists, 'albums': albums}
    return render(request, 'dottify/index.html', context)


# ---------------- ALBUMS ----------------
def album_list(request):
    albums = Album.objects.all()
    return render(request, 'dottify/album_list.html', {'albums': albums})


def album_create(request):
    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save()
            return redirect('album-detail-id', album_id=album.id)
    else:
        form = AlbumForm()
    return render(request, 'dottify/album_form.html', {'form': form})


def album_search(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    q = request.GET.get('q', '')
    albums = Album.objects.filter(title__icontains=q)
    titles = ", ".join(a.title for a in albums)
    return HttpResponse(titles or "No results")


def album_detail_by_id(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    songs = album.song_set.all()

    # rating averages (Sheet D)
    ratings = Rating.objects.filter(album=album, value__isnull=False)
    avg_all = avg_recent = None
    if ratings.exists():
        avg_all = sum(r.value for r in ratings) / ratings.count()
        recent = ratings  # placeholder
        avg_recent = sum(r.value for r in recent) / recent.count()

    context = {
        'album': album,
        'songs': songs,
        'avg_all': avg_all,
        'avg_recent': avg_recent,
    }
    return render(request, 'dottify/album_detail.html', context)


def album_detail_with_slug(request, album_id, slug):
    album = get_object_or_404(Album, pk=album_id)
    expected = slugify(album.title)
    if slug != expected:
        return HttpResponseRedirect(f"/albums/{album_id}/{expected}/")
    return HttpResponse(f"Album: {album.title}")


def album_edit(request, album_id):
    get_object_or_404(Album, pk=album_id)
    return HttpResponse("Edit album")


def album_delete(request, album_id):
    get_object_or_404(Album, pk=album_id)
    return HttpResponse("Delete album")


# ---------------- SONGS ----------------
def song_new(request):
    if request.method == "POST":
        form = SongForm(request.POST)
        if form.is_valid():
            song = form.save()
            return redirect('song-detail', song_id=song.id)
    else:
        form = SongForm()
    return render(request, 'dottify/song_form.html', {'form': form})


def song_detail(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    return render(request, 'dottify/song_detail.html', {'song': song})


def song_list(request):
    songs = Song.objects.all()
    count = songs.count()
    return render(request, 'dottify/song_list.html', {'songs': songs, 'count': count})


def song_edit(request, song_id):
    get_object_or_404(Song, pk=song_id)
    return HttpResponse("Edit song")


def song_delete(request, song_id):
    get_object_or_404(Song, pk=song_id)
    return HttpResponse("Delete song")


# ---------------- PLAYLISTS ----------------
def playlist_list(request):
    """New list view so /playlists/ works."""
    playlists = Playlist.objects.all()
    return render(request, 'dottify/playlist_list.html', {'playlists': playlists})


def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    comments = Comment.objects.filter(playlist=playlist).select_related('user')
    return render(request, 'dottify/playlist_detail.html', {
        'playlist': playlist,
        'comments': comments,
    })


# ---------------- USERS ----------------
def user_detail_redirect(request, user_id):
    duser = get_object_or_404(DottifyUser, pk=user_id)
    target_slug = duser.display_name.lower()
    return redirect('user-detail-slug', user_id=user_id, slug=target_slug)


def user_detail_slug(request, user_id, slug):
    duser = get_object_or_404(DottifyUser, pk=user_id)
    playlists = duser.playlist_set.all()
    correct_slug = duser.display_name.lower()
    if slug != correct_slug:
        return redirect('user-detail-slug', user_id=user_id, slug=correct_slug)
    return render(request, 'dottify/user_detail.html', {'duser': duser, 'playlists': playlists})


# ---------------- HELP ----------------
class HelpForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)


@login_required
def help_view(request):
    initial = {}
    if request.user.is_authenticated:
        initial['email'] = request.user.email
    if request.method == 'POST':
        form = HelpForm(request.POST, initial=initial)
        if form.is_valid():
            return HttpResponse("Support request submitted")
    else:
        form = HelpForm(initial=initial)
    return render(request, 'dottify/help.html', {'form': form})
