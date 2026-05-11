import json
import logging
import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from groq import Groq
from gamebuilder.models import Game
from profiles.models import UserPersona
from .models import GameSession, GameEvent

logger = logging.getLogger(__name__)
_groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY")) if os.environ.get("GROQ_API_KEY") else None


def _append_event(session, turn, kind, content="", image_url="", payload=None):
    return GameEvent.objects.create(
        session=session,
        turn=turn,
        kind=kind,
        content=content,
        image_url=image_url,
        payload_json=payload or {},
    )


def _get_recent_suggestions(session, limit_events=20):
    recent = session.events.filter(kind="SUGGESTIONS").order_by("-created_at")[:limit_events]
    seen = set()
    for ev in recent:
        for s in (ev.payload_json or {}).get("items", []):
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

게임 정보:
  제목: {game_title}
  장르: {game_genre}
  세계관: {world_setting}

플레이어 캐릭터:
{player_info}

규칙:
- 매 응답은 반드시 아래 JSON 형식만 출력한다. 설명이나 마크다운 코드블록 없이.
{{"story": "3~5문장의 장면 묘사나 스토리 진행", "suggestions": ["선택지1", "선택지2", "선택지3"], "info": {{"턴": "T-N", "위치": "현재 장소", "상태": "캐릭터의 현재 감정·상태 한 줄", "소지품": "아이템 또는 돈 정보", "관계": ["NPC명 😊", "NPC명 😐"]}}}}
- story는 한국어 현재형으로, 2인칭 시점으로 작성한다.
- suggestions는 플레이어가 바로 선택할 수 있는 행동 3가지다.
- info.턴은 "T-1", "T-2" 형식으로 현재 턴 번호를 쓴다.
- info.관계는 등장한 NPC만 포함하고, 관계 정도에 따라 😊😐😠 이모지를 붙인다.
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
        prefix = suffix = "*" if ev.kind == "USER_ACTION" else ""
        messages.append({"role": role, "content": f"{prefix}{ev.content}{suffix}"})
    return messages


def _build_player_info(session):
    state = session.state_json or {}
    persona = session.persona
    user_memo = state.get("user_memo", "")

    if persona and persona.content:
        info = f"  페르소나: {persona.title}\n"
        for line in persona.content.strip().splitlines():
            info += f"  {line}\n"
    else:
        name = state.get("user_name") or session.user.username
        info = f"  이름: {name}\n"

    if user_memo:
        info += f"\n  추가 메모: {user_memo}"
    return info.strip()


def _groq_engine(user_text, session, mode):
    if _groq_client is None:
        raise RuntimeError("GROQ_API_KEY not set")

    game = session.game
    player_info = _build_player_info(session)

    system_prompt = _SYSTEM_TEMPLATE.format(
        game_title=game.title,
        game_genre=game.genre,
        world_setting=game.world_setting or "설정 없음",
        player_info=player_info,
    )

    history = _build_history(session)
    user_msg = f"*{user_text}*" if mode == "action" else f'"{user_text}"'
    history.append({"role": "user", "content": user_msg})

    response = _groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}] + history,
        temperature=0.85,
        max_tokens=512,
    )

    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)
    return data.get("story", ""), data.get("suggestions", [])[:3], data.get("info", {})


def _dummy_engine(user_text, session):
    state = session.state_json or {}
    mood = int(state.get("mood", 0))
    base_pool = [
        "주변을 둘러본다.", "상대에게 질문한다.", "조용히 이동한다.",
        "단서를 찾기 위해 한 바퀴 돌아본다.", "상대의 표정을 관찰한다.",
        "대화를 이어가며 정보를 캐낸다.", "일단 침착하게 상황을 정리한다.",
    ]
    story = "짧은 침묵. 네 선택을 기다리는 듯 주변의 공기가 가라앉는다."
    suggestions = _make_suggestions_avoiding_repeat(session, base_pool, k=3)
    info = {"턴": f"T-{session.turn}", "위치": "알 수 없음", "상태": f"기분 {mood:+d}", "소지품": "-", "관계": []}
    return story, info, suggestions


@login_required
@require_http_methods(["GET"])
def game_view(request, game_id):
    game = get_object_or_404(Game, pk=game_id, is_published=True)

    persona_id = request.GET.get("persona_id") or request.session.get("game_persona_id")
    user_memo = request.GET.get("user_memo", request.session.get("game_user_memo", ""))

    session, created = GameSession.objects.get_or_create(
        user=request.user,
        game=game,
    )

    if created:
        persona = None
        if persona_id:
            try:
                persona = UserPersona.objects.get(pk=persona_id, user=request.user)
                session.persona = persona
            except UserPersona.DoesNotExist:
                pass
        session.state_json = {"user_memo": user_memo}
        session.save()
        _append_event(session, session.turn, "STORY_TEXT", content=game.prologue or "게임이 시작됐다.")

    events = session.events.order_by("created_at")
    latest_sugg_ev = session.events.filter(kind="SUGGESTIONS").order_by("-created_at").first()
    latest_suggestions = (latest_sugg_ev.payload_json or {}).get("items", []) if latest_sugg_ev else []

    return render(request, "game/game.html", {
        "game": game,
        "session": session,
        "events": events,
        "game_title": game.title,
        "latest_suggestions": latest_suggestions,
    })


@login_required
@require_http_methods(["POST"])
def game_turn(request, game_id):
    game = get_object_or_404(Game, pk=game_id, is_published=True)
    session = get_object_or_404(GameSession, user=request.user, game=game)

    raw_text = (request.POST.get("message") or "").strip()
    mode = (request.POST.get("mode") or "action").strip()
    user_text = raw_text

    if len(raw_text) >= 2 and raw_text.startswith("*") and raw_text.endswith("*"):
        mode = "action"
        user_text = raw_text[1:-1].strip()
    elif len(raw_text) >= 2 and raw_text.startswith('"') and raw_text.endswith('"'):
        mode = "dialogue"
        user_text = raw_text[1:-1].strip()

    if not user_text:
        return redirect("game:view", game_id=game_id)

    session.turn += 1
    session.save(update_fields=["turn"])

    kind = "USER_DIALOGUE" if mode == "dialogue" else "USER_ACTION"
    _append_event(session, session.turn, kind, content=user_text)

    try:
        story, suggestions, info = _groq_engine(user_text, session, mode)
    except Exception as exc:
        logger.warning("Groq engine failed (%s), using dummy fallback", exc)
        story, info, suggestions = _dummy_engine(user_text, session)

    _append_event(session, session.turn, "STORY_TEXT", content=story)
    if info:
        _append_event(session, session.turn, "INFO_PANEL", payload={"info": info})
    _append_event(session, session.turn, "SUGGESTIONS", payload={"items": suggestions})

    return redirect("game:view", game_id=game_id)
