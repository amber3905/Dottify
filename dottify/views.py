from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django import forms
from .models import Album, Song, Playlist, DottifyUser, Comment, Rating
from .forms import AlbumForm, SongForm


def get_dottify_user_or_none(user):
    """
    Helper used across views.

    Returns the DottifyUser profile if the request user is authenticated,
    otherwise None. This lets us keep the logic for looking up profiles
    in one place.
    """
    if not user.is_authenticated:
        return None
    return DottifyUser.objects.filter(user=user).first()


def index(request):
    """
    Homepage route with role-based content.

    - Anonymous users: show all albums and public playlists only.
    - Logged-in normal users: show only their own playlists.
    - Artist users (in the 'Artist' group): show only their own albums.
    - DottifyAdmin users (in the 'DottifyAdmin' group or superuser):
      show all albums, songs, and playlists.
    """
    user = request.user
    duser = get_dottify_user_or_none(user)
    if not user.is_authenticated:
        albums = Album.objects.all()
        playlists = Playlist.objects.filter(visibility=2)
        return render(
            request,
            'dottify/index.html',
            {'albums': albums, 'playlists': playlists},
        )
    is_dottify_admin = user.is_superuser or user.groups.filter(name="DottifyAdmin").exists()
    is_artist = user.groups.filter(name="Artist").exists()
    if is_dottify_admin:
        albums = Album.objects.all()
        playlists = Playlist.objects.all()
        songs = Song.objects.all()
        return render(
            request,
            'dottify/index.html',
            {'albums': albums, 'playlists': playlists, 'songs': songs},
        )
    if is_artist:
        if duser:
            albums = Album.objects.filter(artist_name=duser.display_name)
        else:
            albums = Album.objects.none()
        return render(
            request,
            'dottify/index.html',
            {'albums': albums},
        )

    if duser:
        playlists = duser.playlist_set.all()
    else:
        playlists = Playlist.objects.none()
    return render(
        request,
        'dottify/index.html',
        {'playlists': playlists},
    )

def album_list(request):
    """
    List view for albums (used by Sheet C and Sheet D requirements).
    """
    albums = Album.objects.all()
    return render(request, 'dottify/album_list.html', {'albums': albums})


@login_required
def album_create(request):
    """
    Create view for albums.

    User must be logged in AND in the Artist or DottifyAdmin group.

    - If not in either group, return 403 Forbidden.
    - If allowed, show the form on GET and create the album on POST.
    """
    user = request.user
    is_artist = user.groups.filter(name="Artist").exists()
    is_dottify_admin = user.groups.filter(name="DottifyAdmin").exists()
    if not (is_artist or is_dottify_admin):
        return HttpResponseForbidden("Forbidden")
    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save()
            return redirect('album-detail-id', album_id=album.id)
    else:
        form = AlbumForm()
    return render(request, 'dottify/album_form.html', {'form': form})

def album_search(request):
    """
    Simple search endpoint for albums.

    - Requires authentication (401 if not logged in).
    - Returns a comma-separated list of matching album titles as plain text.
    This matches the behaviour expected by the provided tests.
    """
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    q = request.GET.get('q', '')
    albums = Album.objects.filter(title__icontains=q)
    titles = ", ".join(a.title for a in albums)
    return HttpResponse(titles or "No results")

def _build_album_detail_context(album):
    """
    Internal helper to build album detail context, including songs and ratings.
    Used by both /albums/<id>/ and /albums/<id>/<slug>/ routes.
    """
    songs = album.song_set.all()

    ratings = Rating.objects.filter(album=album, value__isnull=False)
    avg_all = avg_recent = None
    if ratings.exists():
        avg_all = sum(r.value for r in ratings) / ratings.count()
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent = ratings.filter(user__user__date_joined__gte=seven_days_ago) if ratings.exists() else ratings
        if recent.exists():
            avg_recent = sum(r.value for r in recent) / recent.count()

    return {
        'album': album,
        'songs': songs,
        'avg_all': avg_all,
        'avg_recent': avg_recent,
    }

def album_detail_by_id(request, album_id):
    """
    Detail page for a single album.

    Also calculates:
    - Average rating over all time.
    - Average rating for recent ratings (last 7 days).

    Songs are listed on the page.
    """
    album = get_object_or_404(Album, pk=album_id)
    context = _build_album_detail_context(album)
    return render(request, 'dottify/album_detail.html', context)

def album_detail_with_slug(request, album_id, slug):
    """
    Detail page for a single album using an optional slug in the URL.

    The slug is based on the album title but is NOT validated:
    any slug (or even a wrong slug) will still display the album details.
    """
    album = get_object_or_404(Album, pk=album_id)
    context = _build_album_detail_context(album)
    return render(request, 'dottify/album_detail.html', context)

@login_required
def album_edit(request, album_id):
    """
    Edit an existing album.
    Rules (Sheet D):
    - User must be logged in (enforced by @login_required).
    - User must be in the Artist or DottifyAdmin group.
    - If user is in Artist group, the album must belong to them:
      we treat an album as belonging to an artist if
      album.artist_name == DottifyUser.display_name.
    - Ownership is checked on both GET (when showing the form)
      and POST (when saving changes).
    - If the user is not allowed, return 403 and do NOT save.
    """
    album = get_object_or_404(Album, pk=album_id)
    user = request.user
    duser = get_dottify_user_or_none(user)
    is_artist = user.groups.filter(name="Artist").exists()
    is_dottify_admin = user.is_superuser or user.groups.filter(name="DottifyAdmin").exists()
    if not (is_artist or is_dottify_admin):
        return HttpResponse("Forbidden", status=403)
    if is_artist and (not duser or album.artist_name != duser.display_name):
        return HttpResponse("Forbidden", status=403)
    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            if is_artist and (not duser or album.artist_name != duser.display_name):
                return HttpResponse("Forbidden", status=403)
            form.save()
            return redirect('album-detail-id', album_id=album.id)
    else:
        form = AlbumForm(instance=album)
    return render(request, 'dottify/album_form.html', {'form': form, 'album': album})

@login_required
def album_delete(request, album_id):
    """
    Delete an existing album.
    Rules (Sheet D):
    - User must be logged in.
    - User must be in the DottifyAdmin group OR be the artist who owns the album.
      An album is considered to belong to an artist if:
        album.artist_name == DottifyUser.display_name
    - Permission is checked on both GET (show confirmation)
      and POST (perform delete).
    - If user is not allowed, return 403 and do NOT delete.
    """
    album = get_object_or_404(Album, pk=album_id)
    user = request.user
    duser = get_dottify_user_or_none(user)
    is_artist = user.groups.filter(name="Artist").exists()
    is_dottify_admin = user.is_superuser or user.groups.filter(name="DottifyAdmin").exists()
    owns_album = (duser and album.artist_name == duser.display_name)
    allowed = is_dottify_admin or (is_artist and owns_album)
    if not allowed:
        return HttpResponse("Forbidden", status=403)
    if request.method == "POST":
        album.delete()
        return redirect('album-list')
    return render(request, "dottify/album_confirm_delete.html", {"album": album})

@login_required
def song_new(request):
    """
    Create a new song.
    Rules:
    - User must be logged in.
    - User must be in the Artist or DottifyAdmin group.
    - If user is in Artist group, the chosen album must belong to them
      (album.artist_name == DottifyUser.display_name). This is checked
      on submit (POST). If it does not match, return 403 and do not save.
    """
    user = request.user
    duser = get_dottify_user_or_none(user)
    is_artist = user.groups.filter(name="Artist").exists()
    is_dottify_admin = user.is_superuser or user.groups.filter(name="DottifyAdmin").exists()
    if not (is_artist or is_dottify_admin):
        return HttpResponse("Forbidden", status=403)
    if request.method == "POST":
        form = SongForm(request.POST)
        if form.is_valid():
            song = form.save(commit=False)
            album = song.album
            if is_artist:
                if not duser or album.artist_name != duser.display_name:
                    return HttpResponse("Forbidden", status=403)
            song.save()
            return redirect('song-detail', song_id=song.id)
    else:
        form = SongForm()
    return render(request, 'dottify/song_form.html', {'form': form})

def song_detail(request, song_id):
    """
    Simple song detail page.
    """
    song = get_object_or_404(Song, pk=song_id)
    return render(request, 'dottify/song_detail.html', {'song': song})


def song_list(request):
    """
    List all songs.

    Sheet D requires a 'Total results found: N' counter somewhere a
    song list is displayed; the template uses `count` for this.
    """
    songs = Song.objects.all()
    count = songs.count()
    return render(request, 'dottify/song_list.html', {'songs': songs, 'count': count})


@login_required
def song_edit(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    album = song.album
    user = request.user
    duser = get_dottify_user_or_none(user)
    is_artist = user.groups.filter(name="Artist").exists()
    is_dottify_admin = user.is_superuser or user.groups.filter(name="DottifyAdmin").exists()
    owns_album = duser and album.artist_name == duser.display_name
    allowed = is_dottify_admin or (is_artist and owns_album)
    if not allowed:
        return HttpResponse("Forbidden", status=403)
    if request.method == "POST":
        form = SongForm(request.POST, instance=song)
        if form.is_valid():
            song = form.save()
            return redirect('song-detail', song_id=song.id)
    else:
        form = SongForm(instance=song)
    return render(request, 'dottify/song_form.html', {'form': form, 'song': song})

@login_required
def song_delete(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    album = song.album
    user = request.user
    duser = get_dottify_user_or_none(user)
    is_artist = user.groups.filter(name="Artist").exists()
    is_dottify_admin = user.is_superuser or user.groups.filter(name="DottifyAdmin").exists()
    owns_album = duser and album.artist_name == duser.display_name
    allowed = is_dottify_admin or (is_artist and owns_album)
    if not allowed:
        return HttpResponse("Forbidden", status=403)
    if request.method == "POST":
        song.delete()
        return redirect("/songs/")
    return render(request, "dottify/song_confirm_delete.html", {"song": song})

def playlist_list(request):
    """
    List playlists according to visibility and user roles.

    - Anonymous users: see public playlists only (visibility = 2).
    - Logged-in users (Normal/Artist): see public playlists and playlists they own.
    - DottifyAdmin users: see all playlists regardless of visibility or ownership.
    """
    playlists = Playlist.objects.all()
    user = request.user
    if not user.is_authenticated:
        playlists = playlists.filter(visibility=2)
    else:
        try:
            duser = DottifyUser.objects.get(user=user)
        except DottifyUser.DoesNotExist:
            duser = None
        if user.is_superuser or user.groups.filter(name="DottifyAdmin").exists():
            pass
        else:
            if duser is not None:
                playlists = playlists.filter(
                    Q(visibility=2) | Q(owner=duser)
                )
            else:
                playlists = playlists.filter(visibility=2)
    return render(request, "dottify/playlist_list.html", {"playlists": playlists})

def playlist_detail(request, playlist_id):
    """
    Detail view for a single playlist.

    Private playlists are only visible to their owner (403 otherwise).
    Comments are displayed with their authors' display names.
    """
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    duser = get_dottify_user_or_none(request.user)

    if playlist.visibility == 0:
        if not duser or playlist.owner_id != duser.id:
            return HttpResponse("Forbidden", status=403)

    comments = Comment.objects.filter(playlist=playlist).select_related('user')
    return render(
        request,
        'dottify/playlist_detail.html',
        {'playlist': playlist, 'comments': comments},
    )


def user_detail_redirect(request, user_id):
    """
    Redirect helper that always sends users to the lowercase slug URL.

    This keeps the 'users/<id>/<slug>/' route canonical while still
    accepting the shorter 'users/<id>/' form.
    """
    duser = get_object_or_404(DottifyUser, pk=user_id)
    target_slug = slugify(duser.display_name)
    return redirect('user-detail-slug', user_id=user_id, slug=target_slug)


def user_detail_slug(request, user_id, slug):
    """
    User profile page.

    If the slug is wrong we redirect to the correct one, but we always
    look up the user by numeric id to avoid security issues.
    """
    duser = get_object_or_404(DottifyUser, pk=user_id)
    playlists = duser.playlist_set.all()
    correct_slug = slugify(duser.display_name)
    if slug != correct_slug:
        return redirect('user-detail-slug', user_id=user_id, slug=correct_slug)
    return render(
        request,
        'dottify/user_detail.html',
        {'duser': duser, 'playlists': playlists},
    )

class HelpForm(forms.Form):
    """
    Simple contact form used by the /help route.

    We do not send real email (per the lab sheet); we just validate
    input and return a success message.
    """
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)


@login_required
def help_view(request):
    """
    Help / support route.

    - Only accessible to logged-in users.
    - Prefills the email address from request.user where possible.
    """
    initial = {}
    if request.user.is_authenticated:
        initial['email'] = request.user.email
    if request.method == 'POST':
        form = HelpForm(request.POST, initial=initial)
        if form.is_valid():
            # In a real app we would send mail; here we just acknowledge.
            return HttpResponse("Support request submitted")
    else:
        form = HelpForm(initial=initial)
    return render(request, 'dottify/help.html', {'form': form})
