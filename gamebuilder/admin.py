from django.contrib import admin
from .models import Game, NPC

class NPCInline(admin.TabularInline):
    model = NPC
    extra = 0

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["title", "genre", "created_by", "created_at"]
    inlines = [NPCInline]
