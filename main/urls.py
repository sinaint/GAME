# main/urls.py
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("game/<int:game_id>/detail/", views.game_detail, name="game_detail"),
    path("game/<int:game_id>/comment/", views.add_comment, name="add_comment"),
]
