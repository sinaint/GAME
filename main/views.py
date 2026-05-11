from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from gamebuilder.models import Game
from game.models import GameSession
from profiles.models import UserPersona, UserMemo
from .models import GameComment


def home(request):
    games = Game.objects.filter(is_published=True).select_related("created_by__user_settings").order_by("-created_at")
    recent_sessions = []
    personas = []
    if request.user.is_authenticated:
        recent_sessions = (
            GameSession.objects
            .filter(user=request.user)
            .select_related("game")
            .prefetch_related("events")
            .order_by("-updated_at")[:15]
        )
        personas = UserPersona.objects.filter(user=request.user)
        memos = UserMemo.objects.filter(user=request.user)
    else:
        memos = []
    return render(request, "main/home.html", {
        "games": games,
        "recent_sessions": recent_sessions,
        "personas": personas,
        "memos": memos,
    })


def game_detail(request, game_id):
    game = get_object_or_404(Game, pk=game_id, is_published=True)
    comments = game.comments.select_related("user")
    personas = UserPersona.objects.filter(user=request.user) if request.user.is_authenticated else []
    memos = UserMemo.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, "main/game_detail.html", {
        "game": game,
        "comments": comments,
        "comment_count": comments.count(),
        "personas": personas,
        "memos": memos,
        "play_url": f"/game/{game_id}/play/",
    })


@login_required
@require_POST
def add_comment(request, game_id):
    game = get_object_or_404(Game, pk=game_id, is_published=True)
    content = request.POST.get("content", "").strip()
    if content:
        GameComment.objects.create(game=game, user=request.user, content=content)
    return redirect("main:game_detail", game_id=game_id)
