from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    path("<int:game_id>/play/", views.game_view, name="view"),
    path("<int:game_id>/turn/", views.game_turn, name="turn"),
    path("<int:game_id>/restart/", views.game_restart, name="restart"),
    path("<int:game_id>/persona/", views.game_set_persona, name="set_persona"),
    path("memo/save/", views.memo_save, name="memo_save"),
]
