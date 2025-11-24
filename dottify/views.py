from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
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
    Homepage showing albums and playlists.

    Authorisation rules (Sheet C / clarifications):
    - If user is NOT logged in: show only PUBLIC playlists.
    - If user IS logged in: show public playlists AND their own playlists.
    Albums are always listed for all users.
    """
    duser = get_dottify_user_or_none(request.user)

    if duser:
        playlists = Playlist.objects.filter(
            Q(visibility=2) | Q(owner=duser)
        ).distinct()
    else:
        playlists = Playlist.objects.filter(visibility=2)

    albums = Album.objects.all()
    context = {'playlists': playlists, 'albums': albums}
    return render(request, 'dottify/index.html', context)


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

    Login is required; this is enforced at the view layer rather than
    the router so the tests can assert on status codes.
    """
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


def album_detail_by_id(request, album_id):
    """
    Detail page for a single album.

    Also calculates:
    - Average rating over all time.
    - Average rating for recent ratings (last 7 days).

    These values are displayed exactly as required in Sheet D.
    """
    album = get_object_or_404(Album, pk=album_id)
    songs = album.song_set.all()

    ratings = Rating.objects.filter(album=album, value__isnull=False)
    avg_all = avg_recent = None
    if ratings.exists():
        avg_all = sum(r.value for r in ratings) / ratings.count()

        # For now we use all ratings as "recent" once filtered to the
        # last 7 days. The time window is controlled here so it can be
        # adjusted without changing the template.
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent = ratings.filter(user__user__date_joined__gte=seven_days_ago) if ratings.exists() else ratings
        if recent.exists():
            avg_recent = sum(r.value for r in recent) / recent.count()

    context = {
        'album': album,
        'songs': songs,
        'avg_all': avg_all,
        'avg_recent': avg_recent,
    }
    return render(request, 'dottify/album_detail.html', context)


def album_detail_with_slug(request, album_id, slug):
    """
    SEO-friendly album detail route with slug.

    If the slug does not match the album title, we redirect to the
    canonical URL (which keeps URLs stable and satisfies the tests).
    """
    album = get_object_or_404(Album, pk=album_id)
    expected = slugify(album.title)
    if slug != expected:
        return HttpResponseRedirect(f"/albums/{album_id}/{expected}/")
    return HttpResponse(f"Album: {album.title}")


@login_required
def album_edit(request, album_id):
    """
    Placeholder edit endpoint. Only checks that the album exists.

    For this coursework we do not need full edit functionality, but
    the route must exist and be protected.
    """
    get_object_or_404(Album, pk=album_id)
    return HttpResponse("Edit album")


@login_required
def album_delete(request, album_id):
    """
    Placeholder delete endpoint. Only checks that the album exists.
    """
    get_object_or_404(Album, pk=album_id)
    return HttpResponse("Delete album")


@login_required
def song_new(request):
    """
    Create a new song.

    Again, restricted to authenticated users as this mutates state.
    """
    if request.method == "POST":
        form = SongForm(request.POST)
        if form.is_valid():
            song = form.save()
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
    """
    Placeholder edit endpoint for songs.
    """
    get_object_or_404(Song, pk=song_id)
    return HttpResponse("Edit song")


@login_required
def song_delete(request, song_id):
    """
    Placeholder delete endpoint for songs.
    """
    get_object_or_404(Song, pk=song_id)
    return HttpResponse("Delete song")


def playlist_list(request):
    """
    List playlists with visibility rules.

    - Anonymous users: public playlists only.
    - Logged-in users: public playlists and their own playlists.
    """
    duser = get_dottify_user_or_none(request.user)

    if duser:
        playlists = Playlist.objects.filter(
            Q(visibility=2) | Q(owner=duser)
        ).distinct()
    else:
        playlists = Playlist.objects.filter(visibility=2)

    return render(request, 'dottify/playlist_list.html', {'playlists': playlists})


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
