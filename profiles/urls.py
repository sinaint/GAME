from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("", views.profile_list, name="list"),
    path("create/", views.profile_create, name="create"),
    path("<int:slot>/select/", views.profile_select, name="select"),
]
