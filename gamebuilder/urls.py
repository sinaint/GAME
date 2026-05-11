from django.urls import path
from . import views

app_name = "gamebuilder"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create/", views.game_create, name="create"),
    path("<int:pk>/edit/", views.game_edit, name="edit"),
    path("<int:pk>/delete/", views.game_delete, name="delete"),
    path("<int:pk>/publish/", views.game_toggle_publish, name="toggle_publish"),
    path("<int:pk>/complete/", views.game_complete, name="complete"),
]
