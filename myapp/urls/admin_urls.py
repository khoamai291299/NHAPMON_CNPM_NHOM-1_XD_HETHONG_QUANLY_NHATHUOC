# Tạo mới file này
from django.urls import path
from ..views import admin_view

app_name = "adminpanel"

urlpatterns = [
    path("", admin_view.index, name="index")
]