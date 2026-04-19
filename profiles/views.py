from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import ProfileForm
from .models import Profile


@login_required
def profile_list(request):
    profiles = Profile.objects.filter(user=request.user, is_deleted=False).order_by(
        "slot"
    )
    by_slot = {p.slot: p for p in profiles}

    game_id = request.GET.get("game_id", "1")
    context = {
        "slots": [(n, by_slot.get(n)) for n in range(1, 4)],
        "game_id": game_id,
    }
    return render(request, "profiles/profile_list.html", context)


@login_required
def profile_create(request):
    # 이미 3개면 생성 막기
    active_count = Profile.objects.filter(user=request.user, is_deleted=False).count()
    if active_count >= 3:
        return redirect("profiles:list")

    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user

            # 혹시 같은 슬롯이 이미 있으면 막기(UniqueConstraint가 최종 방어)
            exists = Profile.objects.filter(
                user=request.user,
                slot=profile.slot,
                is_deleted=False,
            ).exists()
            if exists:
                form.add_error("slot", "해당 슬롯은 이미 사용 중입니다.")
            else:
                # 등급은 일단 기본값(C) 유지. 나중에 등급 판정 함수 붙일 예정
                profile.save()
                return redirect("profiles:list")
    else:
        slot = request.GET.get("slot")
        initial = {"slot": slot} if slot in ("1", "2", "3") else {}
        form = ProfileForm(initial=initial)

    return render(request, "profiles/profile_form.html", {"form": form})


@login_required
def profile_select(request, slot: int):
    # 나중에 game 앱과 연결될 "선택된 프로필" 저장
    profile = Profile.objects.filter(
        user=request.user,
        slot=slot,
        is_deleted=False,
    ).first()

    if not profile:
        return redirect("profiles:list")

    try:
        game_id = int(request.GET.get("game_id", 1))
    except (ValueError, TypeError):
        game_id = 1

    request.session["active_profile_id"] = profile.id
    request.session["active_game_id"] = game_id
    return redirect("game:view", profile_id=profile.id)
