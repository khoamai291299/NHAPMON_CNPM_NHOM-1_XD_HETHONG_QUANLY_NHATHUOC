# Create your views here.
from django.shortcuts import render, redirect
from django.db import connection

def index(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, "admin/index.html")


def admin_bill(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/bill.html')

def admin_category(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/category.html')

def admin_customer(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/customer.html')

def admin_employee(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/employee.html')

def admin_permissions(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/permissions.html')

def admin_product(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/product.html')

from myapp.models.role import Role
from django.db.models import Q

def admin_roles(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    search = request.GET.get("search", "")

    if search:
        roles = Role.objects.filter(
            Q(role__icontains=search) |
            Q(role_name__icontains=search)
        )
    else:
        roles = Role.objects.all()

    return render(request, 'admin/roles.html', {
        "roles": roles,
        "search": search
    })


def admin_users(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/users.html')

def admin_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/dashboard.html')

def admin_404(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/404.html')

def admin_500(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/500.html')

from django.contrib import messages
from myapp.models.user import Users
from django.contrib.auth.hashers import check_password

def admin_login(request):
    # Nếu đã login thì vào thẳng dashboard
    if request.session.get("user_id"):
        return redirect("adminpanel:index")

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # 1. Kiểm tra user tồn tại
        try:
            user = Users.objects.select_related("role").get(username=username)
        except Users.DoesNotExist:
            messages.error(request, "Sai username hoặc password")
            return render(request, "admin/login.html")

        # 2. Kiểm tra mật khẩu đúng
        if not user.check_password(password):
            messages.error(request, "Sai username hoặc password")
            return render(request, "admin/login.html")

        # 3. Kiểm tra quyền admin
        # user.role.role = 'admin' hoặc 'seller' hoặc 'warehouse'
        if user.role.role != "admin":  # hoặc admin nếu bạn đặt tên role là admin
            messages.error(request, "Bạn không có quyền truy cập trang quản trị")
            return render(request, "admin/login.html")

        # 4. Lưu session
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        request.session['role'] = user.role.role

        return redirect('adminpanel:index')

    return render(request, "admin/login.html")


def admin_logout(request):
    request.session.flush()   # Xóa toàn bộ session
    return redirect('adminpanel:admin_login')   # Quay về trang đăng nhập

from django.contrib.auth.hashers import make_password

import re

def is_strong_password(pw):
    if len(pw) < 8:
        return False
    if not re.search(r"[A-Z]", pw):
        return False
    if not re.search(r"[a-z]", pw):
        return False
    if not re.search(r"[0-9]", pw):
        return False
    if not re.search(r"[\W_]", pw):  # ký tự đặc biệt
        return False
    return True


def admin_profile(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    user = Users.objects.get(pk=request.session['user_id'])

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()

        user.email = email
        user.phone = phone

        # Nếu có nhập mật khẩu mới
        if password != "":
            if not is_strong_password(password):
                messages.error(request,
                    "Mật khẩu phải có ít nhất 8 ký tự, gồm chữ hoa, chữ thường, số và ký tự đặc biệt."
                )
                return render(request, "admin/profile.html", {"user": user})

            user.password = make_password(password)

        user.save()
        messages.success(request, "Cập nhật thông tin cá nhân thành công.")
        return redirect('adminpanel:admin_profile')

    return render(request, "admin/profile.html", {"user": user})



def admin_base(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/base.html')

from myapp.forms.role_forms import RoleForm
def admin_roles_add(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    if request.method == "POST":
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm quyền thành công.")
            return redirect("adminpanel:admin_roles")
    else:
        form = RoleForm()

    return render(request, "admin/roles_add.html", {"form": form})

def admin_roles_edit(request, role):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    role_obj = Role.objects.get(pk=role)

    if request.method == "POST":
        form = RoleForm(request.POST, instance=role_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật quyền thành công.")
            return redirect("adminpanel:admin_roles")
    else:
        form = RoleForm(instance=role_obj)

    return render(request, "admin/roles_edit.html", {"form": form, "role": role})

def admin_roles_delete(request, role):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    try:
        Role.objects.get(pk=role).delete()
        messages.success(request, "Xóa quyền thành công.")
    except:
        messages.error(request, "Không thể xóa quyền.")

    return redirect("adminpanel:admin_roles")

from myapp.models.medicine_type import TypeMedicine
from django.db.models import Q

def admin_category(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    search = request.GET.get("search", "")

    if search:
        categories = TypeMedicine.objects.filter(
            Q(id__icontains=search) |
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    else:
        categories = TypeMedicine.objects.all()

    return render(request, 'admin/category.html', {
        "categories": categories,
        "search": search
    })
from myapp.forms.type_medicine_form import TypeMedicineForm

def admin_category_add(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    if request.method == "POST":
        form = TypeMedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm phân loại thuốc thành công")
            return redirect("adminpanel:admin_category")
    else:
        form = TypeMedicineForm()

    return render(request, "admin/category_add.html", {"form": form})
def admin_category_edit(request, id):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    category = TypeMedicine.objects.get(pk=id)

    if request.method == "POST":
        form = TypeMedicineForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật phân loại thuốc thành công")
            return redirect("adminpanel:admin_category")
    else:
        form = TypeMedicineForm(instance=category)

    return render(request, "admin/category_edit.html", {"form": form, "id": id})
def admin_category_delete(request, id):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    try:
        TypeMedicine.objects.get(pk=id).delete()
        messages.success(request, "Xóa phân loại thuốc thành công")
    except:
        messages.error(request, "Không thể xóa phân loại thuốc")

    return redirect("adminpanel:admin_category")
