from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    # 프로필 id로 바로 게임 화면 진입
    path("<int:profile_id>/", views.game_view, name="view"),

    # 입력(턴 진행)
    path("<int:profile_id>/turn/", views.game_turn, name="turn"),
]