import json
import logging
import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from groq import Groq
from profiles.models import Profile
from .models import GameSession, GameEvent

logger = logging.getLogger(__name__)
_groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY")) if os.environ.get("GROQ_API_KEY") else None


def _append_event(session, turn, kind, content="", image_url="", payload=None):
    # 이벤트를 저장하는 공통 함수(중복 코드 방지)
    return GameEvent.objects.create(
        session=session,
        turn=turn,
        kind=kind,
        content=content,
        image_url=image_url,
        payload_json=payload or {},
    )


def _get_recent_suggestions(session, limit_events=20):
    recent = session.events.filter(kind="SUGGESTIONS").order_by("-created_at")[
        :limit_events
    ]
    seen = set()
    for ev in recent:
        items = (ev.payload_json or {}).get("items", [])
        for s in items:
            if isinstance(s, str):
                seen.add(s.strip())
    return seen


def _make_suggestions_avoiding_repeat(session, base_pool, k=3):
    seen = _get_recent_suggestions(session)
    filtered = [s for s in base_pool if s.strip() and s.strip() not in seen]
    pool = filtered if len(filtered) >= k else base_pool
    return pool[:k]


_SYSTEM_TEMPLATE = """\
너는 인터랙티브 소설 게임의 내레이터 AI다.
플레이어 캐릭터 정보:
  이름: {name}
  성별: {gender}
  나이: {age}세
  분위기: {vibe}

규칙:
- 매 응답은 반드시 아래 JSON 형식만 출력한다. 설명이나 마크다운 코드블록 없이.
{{"story": "3~5문장의 장면 묘사나 스토리 진행", "suggestions": ["선택지1", "선택지2", "선택지3"]}}
- story는 한국어 현재형으로, 2인칭 시점으로 작성한다.
- suggestions는 플레이어가 바로 선택할 수 있는 행동 3가지다.
"""

_KIND_TO_ROLE = {
    "USER_ACTION": "user",
    "USER_DIALOGUE": "user",
    "STORY_TEXT": "assistant",
    "SUGGESTIONS": None,
    "INFO_PANEL": None,
}


def _build_history(session, limit=10):
    events = (
        session.events
        .filter(kind__in=["USER_ACTION", "USER_DIALOGUE", "STORY_TEXT"])
        .order_by("-created_at")[:limit]
    )
    messages = []
    for ev in reversed(list(events)):
        role = _KIND_TO_ROLE.get(ev.kind)
        if role is None:
            continue
        prefix = "*" if ev.kind == "USER_ACTION" else ""
        suffix = "*" if ev.kind == "USER_ACTION" else ""
        messages.append({"role": role, "content": f"{prefix}{ev.content}{suffix}"})
    return messages


def _groq_engine(user_text, session, mode):
    if _groq_client is None:
        raise RuntimeError("GROQ_API_KEY not set")

    p = session.profile
    system_prompt = _SYSTEM_TEMPLATE.format(
        name=p.name,
        gender=p.gender,
        age=p.age,
        vibe=p.vibe_text or "특별한 분위기 없음",
    )

    history = _build_history(session)

    user_msg = f'*{user_text}*' if mode == "action" else f'"{user_text}"'
    history.append({"role": "user", "content": user_msg})

    response = _groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}] + history,
        temperature=0.85,
        max_tokens=512,
    )

    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)
    story = data.get("story", "")
    suggestions = data.get("suggestions", [])[:3]
    return story, suggestions


def _dummy_engine(user_text, session):
    state = session.state_json or {}
    mood = int(state.get("mood", 0))

    base_pool = [
        "주변을 둘러본다.",
        "상대에게 질문한다.",
        "조용히 이동한다.",
        "단서를 찾기 위해 한 바퀴 돌아본다.",
        "상대의 표정을 관찰한다.",
        "대화를 이어가며 정보를 캐낸다.",
        "일단 침착하게 상황을 정리한다.",
        "뒤로 물러나 안전거리를 만든다.",
        "주머니/가방을 확인한다.",
        "주변 사람들에게 조심스럽게 물어본다.",
    ]

    if "점심" in user_text:
        story = "점심시간이 다가왔다. 복도 끝에서 누군가가 너를 바라본다."
        base_pool = [
            "그래, 같이 가자.",
            "무시하고 혼자 나간다.",
            '이브에게 묻는다: "점심은 어디가 좋지?"',
            "근처 식당 정보를 먼저 찾아본다.",
            "상대의 의도를 확인해본다.",
        ]
        mood += 1
    else:
        story = "짧은 침묵. 네 선택을 기다리는 듯 주변의 공기가 가라앉는다."

    suggestions = _make_suggestions_avoiding_repeat(session, base_pool, k=3)

    info_text = (
        f"turn={session.turn}\n" f"mood={mood}\n" f"profile={session.profile.name}\n"
    )

    state["mood"] = mood
    session.state_json = state
    session.save(update_fields=["state_json"])

    return story, info_text, suggestions


@login_required
def game_home(request):
    profile_id = request.session.get("active_profile_id")
    if not profile_id:
        return redirect("profiles:list")

    profile = Profile.objects.filter(id=profile_id, user=request.user).first()
    if not profile:
        return redirect("profiles:list")

    return render(request, "game/game_home.html", {"profile": profile})


@login_required
@require_http_methods(["GET"])
def game_view(request, profile_id):
    profile = get_object_or_404(
        Profile, id=profile_id, user=request.user, is_deleted=False
    )
    game_id = request.session.get("active_game_id", 1)
    session, created = GameSession.objects.get_or_create(profile=profile, game_id=game_id)

    if created:
        _append_event(session, session.turn, "STORY_TEXT", content="게임이 시작됐다.")

    events = session.events.order_by("created_at")
    return render(
        request,
        "game/game.html",
        {"profile": profile, "session": session, "events": events},
    )


@login_required
@require_http_methods(["POST"])
def game_turn(request, profile_id):
    profile = get_object_or_404(
        Profile, id=profile_id, user=request.user, is_deleted=False
    )
    game_id = request.session.get("active_game_id", 1)
    session, _ = GameSession.objects.get_or_create(profile=profile, game_id=game_id)

    raw_text = (request.POST.get("message") or "").strip()

    mode = (request.POST.get("mode") or "action").strip()
    user_text = raw_text

    if len(raw_text) >= 2 and raw_text.startswith("*") and raw_text.endswith("*"):
        mode = "action"
        user_text = raw_text[1:-1].strip()

    elif len(raw_text) >= 2 and raw_text.startswith('"') and raw_text.endswith('"'):
        mode = "dialogue"
        user_text = raw_text[1:-1].strip()

    # 빈 값이면 그냥 화면으로 복귀 (None 반환 방지)
    if not user_text:
        return redirect("game:view", profile_id=profile_id)

    session.turn += 1
    session.save(update_fields=["turn"])

    if mode == "dialogue":
        _append_event(session, session.turn, "USER_DIALOGUE", content=user_text)
    else:
        _append_event(session, session.turn, "USER_ACTION", content=user_text)

    try:
        story, suggestions = _groq_engine(user_text, session, mode)
        info_text = None
    except Exception as exc:
        logger.warning("Groq engine failed (%s), using dummy fallback", exc)
        story, info_text, suggestions = _dummy_engine(user_text, session)

    _append_event(session, session.turn, "STORY_TEXT", content=story)
    if info_text:
        _append_event(session, session.turn, "INFO_PANEL", content=info_text)
    _append_event(session, session.turn, "SUGGESTIONS", payload={"items": suggestions})

    # 무조건 HttpResponse 반환
    return redirect("game:view", profile_id=profile_id)
