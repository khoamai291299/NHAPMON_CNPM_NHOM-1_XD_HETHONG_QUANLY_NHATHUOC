# Tạo mới file này
from django.urls import path
from ..views import admin_view

app_name = "adminpanel"

urlpatterns = [
    path("login/", admin_view.admin_login, name="admin_login"),
    path('', admin_view.index, name='index'),
    path("bill", admin_view.admin_bill, name = "admin_bill"),
    path("category", admin_view.admin_category, name = "admin_category"),
    path("customer", admin_view.admin_customer, name = "admin_customer"),
    path("employee", admin_view.admin_employee, name = "admin_employee"),
    path("permissions", admin_view.admin_permissions, name = "admin_permissions"),
    path("product", admin_view.admin_product, name = "admin_product"),
    path("roles", admin_view.admin_roles, name = "admin_roles"),
    path("users", admin_view.admin_users, name = "admin_users"),
    path("404", admin_view.admin_404, name = "admin_404"),
    path("500", admin_view.admin_500, name = "admin_500"),
    path('logout/', admin_view.admin_logout, name="admin_logout"),
    path('profile/', admin_view.admin_profile, name="admin_profile"),
    path('base/', admin_view.admin_base, name="admin_base"),
]
