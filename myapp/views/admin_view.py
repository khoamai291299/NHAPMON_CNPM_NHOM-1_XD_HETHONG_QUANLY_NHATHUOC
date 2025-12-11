# Create your views here.
from django.shortcuts import render, redirect
from django.db import connection

def index(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    return render(request, 'admin/index.html')

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

def admin_roles(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/roles.html')

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
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # 1. Kiểm tra user tồn tại
        try:
            user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            messages.error(request, "Sai username hoặc password")
            return render(request, "admin/login.html")

        # 2. Kiểm tra mật khẩu
        if not user.check_password(password):
            messages.error(request, "Sai username hoặc password")
            return render(request, "admin/login.html")

        # 3. Kiểm tra quyền admin
        if user.role != "admin":
            messages.error(request, "Bạn không có quyền truy cập trang quản trị")
            return render(request, "admin/login.html")

        # 4. Lưu session & chuyển trang
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        request.session['role'] = user.role

        return redirect('adminpanel:index')
    return render(request, "admin/login.html")


def admin_logout(request):
    request.session.flush()   # Xóa toàn bộ session
    return redirect('adminpanel:admin_login')   # Quay về trang đăng nhập

def admin_base(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/base.html')