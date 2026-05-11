from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("mypage/", views.mypage, name="mypage"),
    path("memo/create/", views.memo_create, name="memo_create"),
    path("memo/<int:pk>/edit/", views.memo_edit, name="memo_edit"),
    path("memo/<int:pk>/delete/", views.memo_delete, name="memo_delete"),
    path("persona/create/", views.persona_create, name="persona_create"),
    path("persona/<int:pk>/edit/", views.persona_edit, name="persona_edit"),
    path("persona/<int:pk>/delete/", views.persona_delete, name="persona_delete"),
]
