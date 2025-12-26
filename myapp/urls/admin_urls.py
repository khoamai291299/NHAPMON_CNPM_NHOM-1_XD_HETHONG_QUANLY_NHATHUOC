# Tạo mới file này
from django.urls import path
from ..views import admin_view

app_name = "adminpanel"

urlpatterns = [
    path("login/", admin_view.admin_login, name="admin_login"),
    path('', admin_view.index, name='index'),
    path("bill", admin_view.admin_bill, name = "admin_bill"),
    path("bill/create/", admin_view.admin_bill_create, name="admin_bill_create"),
    path(
    "customer/add-from-bill/",
    admin_view.admin_customer_add_from_bill,
    name="admin_customer_add_from_bill"
    ),
    path("ajax/find-customer/", admin_view.ajax_find_customer, name="ajax_find_customer"),
    path("customer", admin_view.admin_customer, name = "admin_customer"),
    path("employee", admin_view.admin_employee, name = "admin_employee"),
    path("permissions", admin_view.admin_permissions, name = "admin_permissions"),
    path("product", admin_view.admin_product, name = "admin_product"),
    path("404", admin_view.admin_404, name = "admin_404"),
    path("500", admin_view.admin_500, name = "admin_500"),
    path('logout/', admin_view.admin_logout, name="admin_logout"),
    path('profile/', admin_view.admin_profile, name="admin_profile"),
    path('base/', admin_view.admin_base, name="admin_base"),
    path("roles/", admin_view.admin_roles, name="admin_roles"),
    path("roles/add/", admin_view.admin_roles_add, name="admin_roles_add"),
    path("roles/edit/<str:role_id>/", admin_view.role_edit, name="role_edit"),
    path("roles/delete/<str:role_id>/", admin_view.role_delete, name="role_delete"),
    path("category", admin_view.admin_category, name="admin_category"),
    path("user/", admin_view.admin_users, name="admin_users"),
    path("manufacturer/", admin_view.admin_manufacturer, name="admin_manufacturer"),
    path("customer_type", admin_view.admin_customer_type, name = "admin_customer_type"),
    path("bill/pdf/<str:bill_id>/", admin_view.admin_bill_pdf, name="admin_bill_pdf"),
    path("api/revenue/", admin_view.revenue_chart_api, name = "revenue_chart_api"),
]
