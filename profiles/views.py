from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import UserMemo, UserPersona, UserSettings


# ── 마이페이지 ──────────────────────────────────────────────────────────────

@login_required
def mypage(request):
    tab = request.GET.get("tab", "info")
    memos = UserMemo.objects.filter(user=request.user)
    personas = UserPersona.objects.filter(user=request.user)
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
    is_creator = request.user.created_games.exists()
    return render(request, "profiles/mypage.html", {
        "tab": tab,
        "memos": memos,
        "personas": personas,
        "user_settings": user_settings,
        "is_creator": is_creator,
    })


@login_required
@require_POST
def nickname_update(request):
    nickname = request.POST.get("nickname", "").strip()
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
    if len(nickname) <= 30:
        user_settings.nickname = nickname
        user_settings.save()
    return redirect("profiles:mypage")


@login_required
def memo_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        if title:
            UserMemo.objects.create(user=request.user, title=title, content=content)
        return redirect("profiles:mypage")
    return render(request, "profiles/memo_form.html", {"obj": None})


@login_required
def memo_edit(request, pk):
    memo = get_object_or_404(UserMemo, pk=pk, user=request.user)
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        if title:
            memo.title = title
            memo.content = content
            memo.save()
        return redirect("profiles:mypage")
    return render(request, "profiles/memo_form.html", {"obj": memo})


@login_required
@require_POST
def memo_delete(request, pk):
    memo = get_object_or_404(UserMemo, pk=pk, user=request.user)
    memo.delete()
    return redirect("profiles:mypage")


@login_required
def persona_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        if title:
            UserPersona.objects.create(
                user=request.user,
                title=title,
                age=request.POST.get("age", "").strip(),
                appearance=request.POST.get("appearance", "").strip(),
                personality=request.POST.get("personality", "").strip(),
                talent=request.POST.get("talent", "").strip(),
                content=request.POST.get("content", "").strip(),
            )
        return redirect("profiles:mypage")
    return render(request, "profiles/persona_form.html", {"obj": None})


@login_required
def persona_edit(request, pk):
    persona = get_object_or_404(UserPersona, pk=pk, user=request.user)
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        if title:
            persona.title = title
            persona.age = request.POST.get("age", "").strip()
            persona.appearance = request.POST.get("appearance", "").strip()
            persona.personality = request.POST.get("personality", "").strip()
            persona.talent = request.POST.get("talent", "").strip()
            persona.content = request.POST.get("content", "").strip()
            persona.save()
        return redirect("profiles:mypage")
    return render(request, "profiles/persona_form.html", {"obj": persona})


@login_required
@require_POST
def persona_delete(request, pk):
    persona = get_object_or_404(UserPersona, pk=pk, user=request.user)
    persona.delete()
    return redirect("profiles:mypage")
