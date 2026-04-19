# main/urls.py
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    # 메인 홈 화면
    path("", views.home, name="home"),
]
