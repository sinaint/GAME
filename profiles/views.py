from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import UserMemo, UserPersona


# ── 마이페이지 ──────────────────────────────────────────────────────────────

@login_required
def mypage(request):
    tab = request.GET.get("tab", "info")
    memos = UserMemo.objects.filter(user=request.user)
    personas = UserPersona.objects.filter(user=request.user)
    return render(request, "profiles/mypage.html", {
        "tab": tab,
        "memos": memos,
        "personas": personas,
    })


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
        content = request.POST.get("content", "").strip()
        if title:
            UserPersona.objects.create(user=request.user, title=title, content=content)
        return redirect("profiles:mypage")
    return render(request, "profiles/persona_form.html", {"obj": None})


@login_required
def persona_edit(request, pk):
    persona = get_object_or_404(UserPersona, pk=pk, user=request.user)
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        if title:
            persona.title = title
            persona.content = content
            persona.save()
        return redirect("profiles:mypage")
    return render(request, "profiles/persona_form.html", {"obj": persona})


@login_required
@require_POST
def persona_delete(request, pk):
    persona = get_object_or_404(UserPersona, pk=pk, user=request.user)
    persona.delete()
    return redirect("profiles:mypage")
