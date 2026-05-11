from django.conf import settings
from django.db import models


class GameSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="game_sessions",
    )
    game = models.ForeignKey(
        "gamebuilder.Game",
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    persona = models.ForeignKey(
        "profiles.UserPersona",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="game_sessions",
    )
    turn = models.PositiveIntegerField(default=0)
    state_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "game"], name="unique_user_game")
        ]


class GameEvent(models.Model):
    KIND_CHOICES = [
        ("USER_ACTION", "유저행동"),
        ("USER_DIALOGUE", "유저대사"),
        ("STORY_TEXT", "스토리텍스트"),
        ("STORY_IMAGE", "스토리이미지"),
        ("INFO_PANEL", "정보패널"),
        ("SUGGESTIONS", "추천답변"),
    ]

    session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name="events",
    )
    turn = models.PositiveIntegerField(default=0)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    content = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)
    payload_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
