from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    path("<int:game_id>/play/", views.game_view, name="view"),
    path("<int:game_id>/turn/", views.game_turn, name="turn"),
]
