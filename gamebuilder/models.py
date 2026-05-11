from django.conf import settings
from django.db import models

GENRE_CHOICES = [
    ("무협", "무협"),
    ("판타지", "판타지"),
    ("SF", "SF"),
    ("로맨스", "로맨스"),
    ("아포칼립스", "아포칼립스"),
    ("현대", "현대"),
]


class Game(models.Model):
    # 기본 정보
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    extra_tags = models.JSONField(default=list, blank=True)
    description = models.CharField(max_length=300, blank=True)

    # 콘텐츠
    world_setting = models.TextField(blank=True)   # 모달 세계관 요약
    detailed_desc = models.TextField(blank=True)   # 상세 페이지 설명
    prologue = models.TextField(blank=True)        # 프롤로그 미리보기

    # 설정
    prompt_template = models.CharField(max_length=100, blank=True, default="기본 템플릿")
    thumb_url = models.CharField(max_length=500, blank=True)

    # 통계 & 공개
    play_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_games",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class NPC(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="npcs")
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, blank=True)
    age = models.PositiveSmallIntegerField(default=20)
    personality = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=50, blank=True)
    relation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.game.title} — {self.name}"
