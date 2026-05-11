from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Game, NPC, GENRE_CHOICES


@login_required
def dashboard(request):
    games = Game.objects.filter(created_by=request.user).order_by("-updated_at")
    return render(request, "gamebuilder/dashboard.html", {"games": games})


@login_required
def game_create(request):
    if request.method == "POST":
        return _save_game(request, game=None)
    return render(request, "gamebuilder/edit.html", {
        "genres": [c[0] for c in GENRE_CHOICES],
        "is_new": True,
    })


@login_required
def game_edit(request, pk):
    game = get_object_or_404(Game, pk=pk, created_by=request.user)
    if request.method == "POST":
        return _save_game(request, game=game)
    return render(request, "gamebuilder/edit.html", {
        "game": game,
        "genres": [c[0] for c in GENRE_CHOICES],
        "is_new": False,
        "extra_tags_str": ", ".join(game.extra_tags or []),
    })


@login_required
@require_POST
def game_delete(request, pk):
    game = get_object_or_404(Game, pk=pk, created_by=request.user)
    game.delete()
    return redirect("gamebuilder:dashboard")


@login_required
@require_POST
def game_toggle_publish(request, pk):
    game = get_object_or_404(Game, pk=pk, created_by=request.user)
    game.is_published = not game.is_published
    game.save(update_fields=["is_published"])
    return redirect("gamebuilder:dashboard")


def _save_game(request, game):
    title = request.POST.get("title", "").strip()
    genre = request.POST.get("genre", "").strip()
    description = request.POST.get("description", "").strip()
    world_setting = request.POST.get("world_setting", "").strip()
    detailed_desc = request.POST.get("detailed_desc", "").strip()
    prologue = request.POST.get("prologue", "").strip()
    prompt_template = request.POST.get("prompt_template", "기본 템플릿").strip()
    thumb_url = request.POST.get("thumb_url", "").strip()
    is_published = request.POST.get("is_published") == "on"
    extra_tags_raw = request.POST.get("extra_tags", "").strip()
    extra_tags = [t.strip() for t in extra_tags_raw.split(",") if t.strip()]

    genres = [c[0] for c in GENRE_CHOICES]

    if not title or not genre:
        return render(request, "gamebuilder/edit.html", {
            "error": "제목과 장르는 필수입니다.",
            "game": game,
            "genres": genres,
            "is_new": game is None,
            "extra_tags_str": extra_tags_raw,
        })

    if game is None:
        game = Game(created_by=request.user)

    game.title = title
    game.genre = genre
    game.extra_tags = extra_tags
    game.description = description
    game.world_setting = world_setting
    game.detailed_desc = detailed_desc
    game.prologue = prologue
    game.prompt_template = prompt_template
    game.thumb_url = thumb_url
    game.is_published = is_published
    game.save()

    return redirect("gamebuilder:dashboard")


@login_required
def game_complete(request, pk):
    game = get_object_or_404(Game, pk=pk, created_by=request.user)
    return render(request, "gamebuilder/complete.html", {"game": game})
