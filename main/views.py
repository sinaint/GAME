from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from gamebuilder.models import Game, GENRE_CHOICES
from game.models import GameSession
from profiles.models import UserPersona, UserMemo, UserSettings
from .models import GameComment, GameBookmark


def home(request):
    q = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()

    games = Game.objects.filter(is_published=True).select_related("created_by__user_settings").order_by("-created_at")
    if q:
        games = games.filter(title__icontains=q)
    if genre:
        games = games.filter(genre=genre)

    genres = [g[0] for g in GENRE_CHOICES]
    recent_sessions = []
    personas = []
    played_game_ids = set()
    show_tutorial = False
    if request.user.is_authenticated:
        recent_sessions = (
            GameSession.objects
            .filter(user=request.user)
            .select_related("game")
            .order_by("-updated_at")[:15]
        )
        played_game_ids = set(
            GameSession.objects.filter(user=request.user).values_list("game_id", flat=True)
        )
        bookmark_game_ids = set(
            GameBookmark.objects.filter(user=request.user).values_list("game_id", flat=True)
        )
        personas = UserPersona.objects.filter(user=request.user)
        memos = UserMemo.objects.filter(user=request.user)
        user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
        if not user_settings.has_seen_tutorial:
            show_tutorial = True
    else:
        memos = []
        bookmark_game_ids = set()
    return render(request, "main/home.html", {
        "games": games,
        "recent_sessions": recent_sessions,
        "personas": personas,
        "memos": memos,
        "played_game_ids": played_game_ids,
        "bookmark_game_ids": bookmark_game_ids,
        "q": q,
        "genre": genre,
        "genres": genres,
        "show_tutorial": show_tutorial,
    })


def game_detail(request, game_id):
    game = get_object_or_404(Game, pk=game_id, is_published=True)
    comments = game.comments.select_related("user")
    personas = UserPersona.objects.filter(user=request.user) if request.user.is_authenticated else []
    memos = UserMemo.objects.filter(user=request.user) if request.user.is_authenticated else []
    is_bookmarked = (
        request.user.is_authenticated
        and GameBookmark.objects.filter(user=request.user, game=game).exists()
    )
    return render(request, "main/game_detail.html", {
        "game": game,
        "comments": comments,
        "comment_count": comments.count(),
        "personas": personas,
        "memos": memos,
        "is_bookmarked": is_bookmarked,
        "play_url": f"/game/{game_id}/play/",
    })


@login_required
@require_POST
def toggle_bookmark(request, game_id):
    game = get_object_or_404(Game, pk=game_id, is_published=True)
    bookmark, created = GameBookmark.objects.get_or_create(user=request.user, game=game)
    if not created:
        bookmark.delete()
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    return redirect(next_url)


@login_required
@require_POST
def add_comment(request, game_id):
    game = get_object_or_404(Game, pk=game_id, is_published=True)
    content = request.POST.get("content", "").strip()
    if content:
        GameComment.objects.create(game=game, user=request.user, content=content)
    return redirect("main:game_detail", game_id=game_id)


@login_required
@require_POST
def tutorial_done(request):
    UserSettings.objects.filter(user=request.user).update(has_seen_tutorial=True)
    return redirect("main:home")
