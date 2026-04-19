from django.db import models


class GameSession(models.Model):
    profile = models.ForeignKey(
        "profiles.Profile",
        on_delete=models.CASCADE,
        related_name="game_sessions",
    )
    game_id = models.IntegerField(default=1)

    turn = models.PositiveIntegerField(default=0)
    state_json = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "game_id"], name="unique_profile_game"
            )
        ]


class GameEvent(models.Model):
    # 화면에 찍히는 이벤트 종류(유저입력/스토리/이미지/INFO/추천답변 등)
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

    # 어떤 턴에서 나온 이벤트인지
    turn = models.PositiveIntegerField(default=0)

    # 이벤트 종류
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)

    # 텍스트 내용(유저 입력, 스토리 문단, INFO 내용 등)
    content = models.TextField(blank=True)

    # 이미지 URL/경로(스토리 이미지용)
    image_url = models.CharField(max_length=500, blank=True)

    # 추천답변처럼 배열이 필요한 경우를 위해 JSON 저장
    payload_json = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)