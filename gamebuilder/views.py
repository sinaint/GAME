from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Game, NPC


@login_required
def game_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        genre = request.POST.get("genre", "").strip()
        description = request.POST.get("description", "").strip()
        world_setting = request.POST.get("world_setting", "").strip()

        if not title or not genre:
            genres = [c[0] for c in Game._meta.get_field("genre").choices]
            return render(request, "gamebuilder/create.html", {
                "error": "제목과 장르는 필수입니다.",
                "prev": request.POST,
                "genres": genres,
            })

        game = Game.objects.create(
            title=title,
            genre=genre,
            description=description,
            world_setting=world_setting,
            created_by=request.user,
        )

        npc_names        = request.POST.getlist("npc_name")
        npc_genders      = request.POST.getlist("npc_gender")
        npc_ages         = request.POST.getlist("npc_age")
        npc_personalities = request.POST.getlist("npc_personality")
        npc_roles        = request.POST.getlist("npc_role")
        npc_relations    = request.POST.getlist("npc_relation")

        for i, name in enumerate(npc_names):
            if not name.strip():
                continue
            try:
                age = int(npc_ages[i])
            except (IndexError, ValueError):
                age = 20
            NPC.objects.create(
                game=game,
                name=name.strip(),
                gender=npc_genders[i] if i < len(npc_genders) else "",
                age=age,
                personality=npc_personalities[i] if i < len(npc_personalities) else "",
                role=npc_roles[i] if i < len(npc_roles) else "",
                relation=npc_relations[i] if i < len(npc_relations) else "",
            )

        return redirect("gamebuilder:complete", pk=game.pk)

    genres = [c[0] for c in Game._meta.get_field("genre").choices]
    return render(request, "gamebuilder/create.html", {"genres": genres})


@login_required
def game_complete(request, pk):
    game = get_object_or_404(Game, pk=pk, created_by=request.user)
    return render(request, "gamebuilder/complete.html", {"game": game})
