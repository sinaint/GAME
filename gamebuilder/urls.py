from django.urls import path
from . import views

app_name = "gamebuilder"

urlpatterns = [
    path("create/", views.game_create, name="create"),
    path("<int:pk>/complete/", views.game_complete, name="complete"),
]
