from django.conf import settings
from django.db import models

GENRE_CHOICES = [
    ("판타지", "판타지"),
    ("무협", "무협"),
    ("SF", "SF"),
    ("로맨스", "로맨스"),
    ("아포칼립스", "아포칼립스"),
]


class Game(models.Model):
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    world_setting = models.TextField(blank=True)
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
