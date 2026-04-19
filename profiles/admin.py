from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # 목록에서 바로 보이게
    list_display = (
        "id",
        "user",
        "slot",
        "name",
        "gender",
        "age",
        "face_grade",
        "body_grade",
        "vibe_grade",
        "is_deleted",
        "created_at",
    )
    list_filter = ("gender", "is_deleted", "face_grade", "body_grade", "vibe_grade")
    search_fields = ("name", "user__username", "face_text", "body_text", "vibe_text")
