# Create your views here.
from django.shortcuts import render, redirect
from django.db import connection

def index(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, "admin/index.html")


from myapp.models.bill import Bill

def admin_bill(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    bills = (
        Bill.objects
        .select_related("cid", "eid")
        .order_by("-dateOfcreate")
    )

    return render(request, "admin/bill.html", {
        "bills": bills
    })


def admin_category(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/category.html')


from myapp.models.employee import Employee
from myapp.models.department import Department
from myapp.models.position import Position

def admin_employee(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ===== THÊM / SỬA =====
    if request.method == "POST":
        emp_id = request.POST.get("id")

        data = {
            "name": request.POST.get("name"),
            "phone": request.POST.get("phone"),
            "sex": request.POST.get("sex") == "1",
            "salary": request.POST.get("salary"),
            "did_id": request.POST.get("did"),
            "pid_id": request.POST.get("pid"),
        }

        if emp_id:  # SỬA
            Employee.objects.filter(id=emp_id).update(**data)
            messages.success(request, "Cập nhật nhân viên thành công")
        else:       # THÊM
            data["id"] = request.POST.get("id_new")
            Employee.objects.create(**data)
            messages.success(request, "Thêm nhân viên thành công")

        return redirect("adminpanel:admin_employee")

    # ===== XÓA =====
    delete_id = request.GET.get("delete")
    if delete_id:
        Employee.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa nhân viên thành công")
        return redirect("adminpanel:admin_employee")

    employees = Employee.objects.select_related("did", "pid").all()
    departments = Department.objects.all()
    positions = Position.objects.all()

    return render(request, "admin/employee.html", {
        "employees": employees,
        "departments": departments,
        "positions": positions
    })


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


# Hiển thị danh sách Roles + Tìm kiếm
from myapp.models.role import Role
from django.db.models import Q

def admin_roles(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    search = request.GET.get("search", "").strip()

    roles = Role.objects.all()

    if search != "":
        roles = roles.filter(
            Q(role__icontains=search) |
            Q(role_name__icontains=search)
        )

    return render(request, "admin/roles.html", {
        "roles": roles,
        "search": search
    })

# Chức năng Thêm Role
def role_add(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    if request.method == "POST":
        role = request.POST.get("role").strip()
        role_name = request.POST.get("role_name").strip()
        status = request.POST.get("status").strip()

        if Role.objects.filter(role=role).exists():
            messages.error(request, "Mã quyền đã tồn tại!")
            return redirect("adminpanel:role_add")

        Role.objects.create(
            role=role,
            role_name=role_name,
            status=status
        )

        messages.success(request, "Thêm quyền thành công")
        return redirect("adminpanel:admin_roles")

    return render(request, "admin/roles_add.html")

def role_edit(request, role_id):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    role = Role.objects.get(role=role_id)

    if request.method == "POST":
        role.role_name = request.POST.get("role_name")
        role.status = request.POST.get("status")
        role.save()

        messages.success(request, "Cập nhật quyền thành công")
        return redirect("adminpanel:admin_roles")

    return render(request, "admin/roles_edit.html", {"role": role})

def role_delete(request, role_id):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    role = Role.objects.get(role=role_id)
    role.delete()
    messages.success(request, "Xóa quyền thành công")

    return redirect("adminpanel:admin_roles")

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
from django.contrib import messages
from myapp.models.medicine_type import TypeMedicine
from django.db.models import Q

def admin_category(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ===== THÊM / SỬA =====
    if request.method == "POST":
        cid = request.POST.get("id")          # có id → sửa
        cid_new = request.POST.get("id_new")  # không có id → thêm
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        # Validate
        if not cid and TypeMedicine.objects.filter(id=cid_new).exists():
            messages.error(request, "Mã phân loại đã tồn tại")
            return redirect("adminpanel:admin_category")

        if TypeMedicine.objects.filter(name=name).exclude(id=cid).exists():
            messages.error(request, "Tên phân loại đã tồn tại")
            return redirect("adminpanel:admin_category")

        if cid:  # ===== SỬA =====
            TypeMedicine.objects.filter(id=cid).update(
                name=name,
                description=description
            )
            messages.success(request, "Cập nhật phân loại thành công")
        else:    # ===== THÊM =====
            TypeMedicine.objects.create(
                id=cid_new,
                name=name,
                description=description
            )
            messages.success(request, "Thêm phân loại thành công")

        return redirect("adminpanel:admin_category")

    # ===== XÓA =====
    delete_id = request.GET.get("delete")
    if delete_id:
        try:
            TypeMedicine.objects.get(id=delete_id).delete()
            messages.success(request, "Xóa phân loại thành công")
        except:
            messages.error(request, "Không thể xóa phân loại")
        return redirect("adminpanel:admin_category")

    # ===== DANH SÁCH =====
    search = request.GET.get("search", "")
    categories = TypeMedicine.objects.all()

    if search:
        categories = categories.filter(
            Q(id__icontains=search) |
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    return render(request, "admin/category.html", {
        "categories": categories,
        "search": search
    })

from django.shortcuts import render, redirect
from django.contrib import messages

from myapp.models.customer import Customer
from myapp.models.customer_type import TypeCustomer
import re

def generate_customer_id():
    last = Customer.objects.filter(id__startswith="CUS").order_by("-id").first()
    if not last:
        return "CUS001"

    match = re.search(r"CUS(\d+)", last.id)
    number = int(match.group(1)) if match else 0
    return f"CUS{number + 1:03d}"


def admin_customer(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ===== THÊM / SỬA =====
    if request.method == "POST":
        cid = request.POST.get("id")  # có id → sửa
        phone = request.POST.get("phone", "").strip()

        # ===== CHECK TRÙNG SĐT =====
        phone_qs = Customer.objects.filter(phone=phone)
        if cid:
            phone_qs = phone_qs.exclude(id=cid)

        if phone and phone_qs.exists():
            messages.error(request, "Số điện thoại đã tồn tại.")
            return redirect("adminpanel:admin_customer")

        # ===== SỬA =====
        if cid:
            Customer.objects.filter(id=cid).update(
                name=request.POST.get("name"),
                phone=phone,
                address=request.POST.get("address"),
                tid_id=request.POST.get("tid")   # cho đổi loại KH
            )
            messages.success(request, "Cập nhật khách hàng thành công")
            return redirect("adminpanel:admin_customer")

        # ===== THÊM (MẶC ĐỊNH KHÁCH THƯỜNG) =====
        try:
            normal_type = TypeCustomer.objects.get(id="TC01")
        except TypeCustomer.DoesNotExist:
            messages.error(request, "Chưa cấu hình loại 'Khách thường'")
            return redirect("adminpanel:admin_customer")

        Customer.objects.create(
            id=generate_customer_id(),
            name=request.POST.get("name"),
            phone=phone,
            address=request.POST.get("address"),
            tid=normal_type,     # 👈 MẶC ĐỊNH
            totalExpenditure=0,
            cumulativePoints=0
        )

        messages.success(request, "Thêm khách hàng thành công")
        return redirect("adminpanel:admin_customer")

    # ===== XÓA =====
    delete_id = request.GET.get("delete")
    if delete_id:
        Customer.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa khách hàng thành công")
        return redirect("adminpanel:admin_customer")

    customers = Customer.objects.select_related("tid").all()
    customer_types = TypeCustomer.objects.all()

    return render(request, "admin/customer.html", {
        "customers": customers,
        "customer_types": customer_types
    })



from myapp.models.manufacturer import Manufacturer

def admin_manufacturer(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ===== THÊM / SỬA =====
    if request.method == "POST":
        mid = request.POST.get("id")          # có id → sửa
        mid_new = request.POST.get("id_new")  # không có id → thêm
        name = request.POST.get("name", "").strip()
        country = request.POST.get("country", "").strip()

        # Validate
        if not mid and Manufacturer.objects.filter(id=mid_new).exists():
            messages.error(request, "Mã nhà sản xuất đã tồn tại")
            return redirect("adminpanel:admin_manufacturer")

        if Manufacturer.objects.filter(name=name).exclude(id=mid).exists():
            messages.error(request, "Tên nhà sản xuất đã tồn tại")
            return redirect("adminpanel:admin_manufacturer")

        if mid:  # ===== SỬA =====
            Manufacturer.objects.filter(id=mid).update(
                name=name,
                country=country
            )
            messages.success(request, "Cập nhật nhà sản xuất thành công")
        else:    # ===== THÊM =====
            Manufacturer.objects.create(
                id=mid_new,
                name=name,
                country=country
            )
            messages.success(request, "Thêm nhà sản xuất thành công")

        return redirect("adminpanel:admin_manufacturer")

    # ===== XÓA =====
    delete_id = request.GET.get("delete")
    if delete_id:
        try:
            Manufacturer.objects.get(id=delete_id).delete()
            messages.success(request, "Xóa nhà sản xuất thành công")
        except:
            messages.error(request, "Không thể xóa nhà sản xuất")
        return redirect("adminpanel:admin_manufacturer")

    # ===== DANH SÁCH =====
    manufacturers = Manufacturer.objects.all()

    return render(request, "admin/manufacturer.html", {
        "manufacturer": manufacturers
    })
  from ..models.user import Users
from ..models.employee import Employee
from ..models.role import Role

def admin_users(request):

    # ===== DELETE =====
    delete_id = request.GET.get("delete")
    if delete_id:
        Users.objects.filter(id=delete_id).delete()
        messages.success(request, "Đã xóa tài khoản")
        return redirect("adminpanel:admin_users")

    # ===== ADD USER =====
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        eid = request.POST.get("eid")
        role = request.POST.get("role")

        if Users.objects.filter(username=username).exists():
            messages.error(request, "Username đã tồn tại")
            return redirect("adminpanel:admin_users")

        user = Users(
            username=username,
            email=email,
            phone=phone,
            eid_id=eid,
            role_id=role,
            status="active"
        )
        user.set_password(password)
        user.status = "active"
        user.save()

        messages.success(request, "Thêm tài khoản thành công")
        return redirect("adminpanel:admin_users")

    # ===== GET DATA =====
    context = {
        "users": Users.objects.select_related("eid", "role"),
        "employees": Employee.objects.all(),
        "roles": Role.objects.all()
    }

    return render(request, "admin/users.html", context)
