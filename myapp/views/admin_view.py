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

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, password_hash, role
                FROM users
                WHERE username=%s AND password_hash=%s AND is_active=1
            """, [username, password])
            
            user = cursor.fetchone()

        if user:
            request.session['user_id'] = user[0]
            request.session['username'] = user[1]
            request.session['role'] = user[3]
            return redirect('adminpanel:index')

        return render(request, 'admin/login.html', {
            'error': 'Sai username hoặc password'
        })
    return render(request, 'admin/login.html')