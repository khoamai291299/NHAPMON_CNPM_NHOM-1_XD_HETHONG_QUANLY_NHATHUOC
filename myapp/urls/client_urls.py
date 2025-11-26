# Tạo mới file này
from django.urls import path
from ..views import client_view

app_name = "client"

urlpatterns = [
    path("", client_view.home, name="home"),
]