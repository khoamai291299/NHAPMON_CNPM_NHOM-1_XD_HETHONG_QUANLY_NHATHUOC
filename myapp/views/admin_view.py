# Create your views here.
from django.shortcuts import render, redirect
from django.db import connection

def index(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, "admin/index.html")

def require_admin_login(request):
    user_id = request.session.get("user_id")
    eid = request.session.get("eid")

    if not user_id or not eid:
        request.session.flush()
        return None

    return eid


import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db import DataError
from myapp.models.employee import Employee
from myapp.models.department import Department
from myapp.models.position import Position


def generate_employee_id():
    last_emp = Employee.objects.filter(id__startswith="EMP").order_by("-id").first()
    if not last_emp:
        return "EMP001"

    match = re.search(r"EMP(\d+)", last_emp.id)
    number = int(match.group(1)) if match else 0
    return f"EMP{number + 1:03d}"


def admin_employee(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ================= POST =================
    if request.method == "POST":
        eid = request.POST.get("id")
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        sex = request.POST.get("sex")
        salary = request.POST.get("salary", "").strip()
        did = request.POST.get("did")
        pid = request.POST.get("pid")

        errors = []

        # ===== VALIDATE NAME =====
        if not name:
            errors.append("Họ tên không được để trống")
        elif len(name) > 50:
            errors.append("Họ tên không được quá 50 ký tự")

        # ===== VALIDATE PHONE =====
        if not phone:
            errors.append("Số điện thoại không được để trống")
        elif not phone.isdigit():
            errors.append("Số điện thoại chỉ được chứa chữ số")
        elif len(phone) > 10 or len(phone) < 10 :
            errors.append("Số điện thoại phải có 10 chữ số")
       
        else:
            phone_qs = Employee.objects.filter(phone=phone)
            if eid:
                phone_qs = phone_qs.exclude(id=eid)
            if phone_qs.exists():
                errors.append("Số điện thoại đã tồn tại")

        # ===== VALIDATE SEX =====
        if sex not in ("0", "1"):
            errors.append("Giới tính không hợp lệ")

        # ===== VALIDATE SALARY =====
        if not salary:
            errors.append("Lương không được để trống")
        else:
            try:
                salary = float(salary)
                if salary <= 0:
                    errors.append("Lương phải lớn hơn 0")
            except ValueError:
                errors.append("Lương phải là số")

        # ===== VALIDATE FK =====
        if not Department.objects.filter(id=did).exists():
            errors.append("Bộ phận không tồn tại")

        if not Position.objects.filter(id=pid).exists():
            errors.append("Chức vụ không tồn tại")

        # ===== NẾU CÓ LỖI =====
        if errors:
            for e in errors:
                messages.error(request, e)

            return render(request, "admin/employee.html", {
                "employees": Employee.objects.select_related("did", "pid"),
                "departments": Department.objects.all(),
                "positions": Position.objects.all(),
                "edit_employee": get_object_or_404(Employee, id=eid) if eid else None,
                "show_modal": True,
                "keyword": request.GET.get("q", "")
            })

        # ===== SAVE =====
        try:
            if eid:
                employee = get_object_or_404(Employee, id=eid)
                employee.name = name
                employee.phone = phone
                employee.sex = (sex == "1")
                employee.salary = salary
                employee.did_id = did
                employee.pid_id = pid
                employee.save()
                messages.success(request, "Cập nhật nhân viên thành công")
            else:
                Employee.objects.create(
                    id=generate_employee_id(),
                    name=name,
                    phone=phone,
                    sex=(sex == "1"),
                    salary=salary,
                    did_id=did,
                    pid_id=pid
                )
                messages.success(request, "Thêm nhân viên thành công")

        except DataError:
            messages.error(request, "Dữ liệu không hợp lệ")
            return render(request, "admin/employee.html", {
                "employees": Employee.objects.select_related("did", "pid"),
                "departments": Department.objects.all(),
                "positions": Position.objects.all(),
                "edit_employee": get_object_or_404(Employee, id=eid) if eid else None,
                "show_modal": True,
                "keyword": ""
            })

        return redirect("adminpanel:admin_employee")

    # ================= DELETE =================
    delete_id = request.GET.get("delete")
    if delete_id:
        Employee.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa nhân viên thành công")
        return redirect("adminpanel:admin_employee")

    # ================= SEARCH =================
    keyword = request.GET.get("q", "").strip()
    employees = Employee.objects.select_related("did", "pid")

    if keyword:
        employees = employees.filter(
            Q(name__icontains=keyword) |
            Q(phone__icontains=keyword) |
            Q(pid__name__icontains=keyword) |
            Q(did__name__icontains=keyword)
        )

    edit_id = request.GET.get("edit")
    edit_employee = get_object_or_404(Employee, id=edit_id) if edit_id else None

    return render(request, "admin/employee.html", {
        "employees": employees,
        "departments": Department.objects.all(),
        "positions": Position.objects.all(),
        "edit_employee": edit_employee,
        "keyword": keyword,
        "show_modal": True if edit_employee else False
    })



def admin_permissions(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    return render(request, 'admin/permissions.html')

import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db import DataError

from myapp.models.medicine import Medicine


# ===============================
# AUTO GENERATE MEDICINE ID
# MED001, MED002, ...
# ===============================
def generate_medicine_id():
    last_med = Medicine.objects.filter(id__startswith="MED").order_by("-id").first()
    if not last_med:
        return "MED001"

    match = re.search(r"MED(\d+)", last_med.id)
    number = int(match.group(1)) if match else 0
    return f"MED{number + 1:03d}"


def admin_product(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')
    
    # ================= POST (ADD / EDIT) =================
    if request.method == "POST":
        mid_pk = request.POST.get("id")          # id thuốc (khi sửa)
        name = request.POST.get("name", "").strip()
        unit = request.POST.get("unit", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        importPrice = request.POST.get("importPrice", "").strip()
        sellingPrice = request.POST.get("sellingPrice", "").strip()
        tid = request.POST.get("tid")             # loại thuốc
        mid = request.POST.get("mid")             # nhà sản xuất

        errors = []

        # ===== VALIDATE =====
        if not name:
            errors.append("Tên thuốc không được để trống")
        if not tid:
            errors.append("Vui lòng chọn loại thuốc")
        if not mid:
            errors.append("Vui lòng chọn nhà sản xuất")

        try:
            quantity = int(quantity)
            if quantity < 0:
                errors.append("Số lượng phải ≥ 0")
        except:
            errors.append("Số lượng phải là số")

        try:
            importPrice = int(importPrice)
            sellingPrice = int(sellingPrice)
        except:
            errors.append("Giá phải là số")

        # ===== CÓ LỖI =====
        if errors:
            for e in errors:
                messages.error(request, e)

            return render(request, "admin/product.html", {
                "medicines": Medicine.objects.all(),
                "medicine_type": TypeMedicine.objects.all(),
                "manufacturers": Manufacturer.objects.all(),
                "edit_medicine": get_object_or_404(Medicine, id=mid_pk) if mid_pk else None,
                "show_modal": True,
                "keyword": request.GET.get("q", "")
            })

        # ===== SAVE =====
        try:
            if mid_pk:
                # UPDATE
                medicine = get_object_or_404(Medicine, id=mid_pk)
                medicine.name = name
                medicine.unit = unit
                medicine.quantity = quantity
                medicine.importPrice = importPrice
                medicine.sellingPrice = sellingPrice
                medicine.tid_id = tid
                medicine.mid_id = mid
                medicine.save()
                messages.success(request, "Cập nhật thuốc thành công")
            else:
                # CREATE
                Medicine.objects.create(
                    id=generate_medicine_id(),
                    name=name,
                    unit=unit,
                    quantity=quantity,
                    importPrice=importPrice,
                    sellingPrice=sellingPrice,
                    tid_id=tid,
                    mid_id=mid
                )
                messages.success(request, "Thêm thuốc thành công")

        except DataError:
            messages.error(request, "Dữ liệu không hợp lệ")

        return redirect("adminpanel:admin_product")

    # ================= DELETE =================
    delete_id = request.GET.get("delete")
    if delete_id:
        Medicine.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa thuốc thành công")
        return redirect("adminpanel:admin_product")

    # ================= SEARCH =================
    keyword = request.GET.get("q", "").strip()
    medicines = Medicine.objects.all()

    if keyword:
        medicines = medicines.filter(
            Q(id__icontains=keyword) |
            Q(name__icontains=keyword) |
            Q(tid__name__icontains=keyword) |
            Q(mid__name__icontains=keyword)
        )

    # ================= EDIT =================
    edit_id = request.GET.get("edit")
    edit_medicine = get_object_or_404(Medicine, id=edit_id) if edit_id else None

    # ================= RENDER =================
    return render(request, "admin/product.html", {
        "medicines": medicines,
        "medicine_type": TypeMedicine.objects.all(),
        "manufacturers": Manufacturer.objects.all(),
        "edit_medicine": edit_medicine,
        "keyword": keyword,
        "show_modal": True if edit_medicine else False
    })

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

    # Nếu đã login thì không cho login lại
    if request.session.get("user_id"):
        return redirect("adminpanel:index")

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            user = Users.objects.select_related("role", "eid").get(username=username)
        except Users.DoesNotExist:
            messages.error(request, "Sai username hoặc password")
            return render(request, "admin/login.html")

        if not user.check_password(password):
            messages.error(request, "Sai username hoặc password")
            return render(request, "admin/login.html")

        if user.status != "active":
            messages.error(request, "Tài khoản đã bị khóa")
            return render(request, "admin/login.html")

        if user.role.role_name != "Admin":
            messages.error(request, "Bạn không có quyền truy cập trang quản trị")
            return render(request, "admin/login.html")

        # ⚠️ USER PHẢI CÓ NHÂN VIÊN
        if not user.eid:
            messages.error(request, "Tài khoản chưa gán nhân viên")
            return render(request, "admin/login.html")

        # 🔥 XÓA SẠCH SESSION CŨ
        request.session.flush()

        # 🔐 SET SESSION ĐẦY ĐỦ
        request.session["user_id"] = user.id
        request.session["eid"] = user.eid.id
        request.session["username"] = user.username
        request.session["role"] = user.role.role_name

        return redirect("adminpanel:index")

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


import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from myapp.models.medicine_type import TypeMedicine

# AUTO GENERATE CATEGORY ID
# TYP_MED001, TYP_MED002, ...

def generate_category_id():
    last_cat = (
        TypeMedicine.objects
        .filter(id__startswith="TYP_MED")
        .order_by("-id")
        .first()
    )

    if not last_cat:
        return "TYP_MED001"

    match = re.search(r"TYP_MED(\d+)", last_cat.id)
    number = int(match.group(1)) if match else 0

    return f"TYP_MED{number + 1:03d}"

def admin_category(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ================= POST (ADD / EDIT) =================
    if request.method == "POST":
        cid = request.POST.get("id")  # có id → sửa
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        errors = []

        # ===== VALIDATE =====
        if not name:
            errors.append("Tên phân loại không được để trống")

        if TypeMedicine.objects.filter(name=name).exclude(id=cid).exists():
            errors.append("Tên phân loại đã tồn tại")

        # ===== CÓ LỖI =====
        if errors:
            for e in errors:
                messages.error(request, e)

            return render(request, "admin/category.html", {
                "categories": TypeMedicine.objects.all(),
                "edit_category": get_object_or_404(TypeMedicine, id=cid) if cid else None,
                "show_modal": True
            })

        # ===== SAVE =====
        if cid:
            # UPDATE
            category = get_object_or_404(TypeMedicine, id=cid)
            category.name = name
            category.description = description
            category.save()
            messages.success(request, "Cập nhật phân loại thành công")
        else:
            # CREATE (AUTO ID)
            TypeMedicine.objects.create(
                id=generate_category_id(),
                name=name,
                description=description
            )
            messages.success(request, "Thêm phân loại thành công")

        return redirect("adminpanel:admin_category")

    # ================= DELETE =================
    delete_id = request.GET.get("delete")
    if delete_id:
        TypeMedicine.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa phân loại thành công")
        return redirect("adminpanel:admin_category")

    # ================= SEARCH =================
    keyword = request.GET.get("q", "").strip()
    categories = TypeMedicine.objects.all()

    if keyword:
        categories = categories.filter(
            Q(id__icontains=keyword) |
            Q(name__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    # ================= EDIT =================
    edit_id = request.GET.get("edit")
    edit_category = get_object_or_404(TypeMedicine, id=edit_id) if edit_id else None

    # ================= RENDER =================
    return render(request, "admin/category.html", {
        "categories": categories,
        "edit_category": edit_category,
        "keyword": keyword,
        "show_modal": True if edit_category else False
    })


import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db import DataError

from myapp.models.customer import Customer
from myapp.models.customer_type import TypeCustomer


# ===== AUTO ID =====
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

    # ================= POST =================
    if request.method == "POST":
        cid = request.POST.get("id")
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        tid = request.POST.get("tid")

        errors = []

        # ===== VALIDATE NAME =====
        if not name:
            errors.append("Tên khách hàng không được để trống")
        elif len(name) > 30:
            errors.append("Tên khách hàng không được quá 30 ký tự")

        # ===== VALIDATE PHONE =====
        if not phone:
            errors.append("Số điện thoại không được để trống")
        elif not phone.isdigit():
            errors.append("Số điện thoại chỉ được chứa chữ số")
        elif len(phone) != 10:
            errors.append("Số điện thoại phải có 10 chữ số")
        else:
            phone_qs = Customer.objects.filter(phone=phone)
            if cid:
                phone_qs = phone_qs.exclude(id=cid)
            if phone_qs.exists():
                errors.append("Số điện thoại đã tồn tại")

        # ===== VALIDATE TYPE (chỉ khi sửa) =====
        if cid and tid and not TypeCustomer.objects.filter(id=tid).exists():
            errors.append("Loại khách hàng không tồn tại")

        # ===== NẾU CÓ LỖI =====
        if errors:
            for e in errors:
                messages.error(request, e)

            return render(request, "admin/customer.html", {
                "customers": Customer.objects.select_related("tid"),
                "customer_types": TypeCustomer.objects.all(),
                "edit_customer": get_object_or_404(Customer, id=cid) if cid else None,
                "show_modal": True,
                "search": request.GET.get("search", "")
            })

        # ===== SAVE =====
        try:
            # ----- UPDATE -----
            if cid:
                customer = get_object_or_404(Customer, id=cid)
                customer.name = name
                customer.phone = phone
                customer.address = address

                if tid:
                    customer.tid_id = tid

                customer.save()
                messages.success(request, "Cập nhật khách hàng thành công")

            # ----- CREATE -----
            else:
                try:
                    normal_type = TypeCustomer.objects.get(id="TYP_CUS001")
                except TypeCustomer.DoesNotExist:
                    messages.error(request, "Chưa cấu hình loại 'Khách thường'")
                    return redirect("adminpanel:admin_customer")

                Customer.objects.create(
                    id=generate_customer_id(),
                    name=name,
                    phone=phone,
                    address=address,
                    tid=normal_type,
                    totalExpenditure=0,
                    cumulativePoints=0
                )
                messages.success(request, "Thêm khách hàng thành công")

        except DataError:
            messages.error(request, "Dữ liệu không hợp lệ")
            return render(request, "admin/customer.html", {
                "customers": Customer.objects.select_related("tid"),
                "customer_types": TypeCustomer.objects.all(),
                "edit_customer": get_object_or_404(Customer, id=cid) if cid else None,
                "show_modal": True,
                "search": ""
            })

        return redirect("adminpanel:admin_customer")

    # ================= DELETE =================
    delete_id = request.GET.get("delete")
    if delete_id:
        Customer.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa khách hàng thành công")
        return redirect("adminpanel:admin_customer")

    # ================= SEARCH =================
    search = request.GET.get("search", "").strip()
    customers = Customer.objects.select_related("tid")

    if search:
        customers = customers.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(address__icontains=search) |
            Q(tid__name__icontains=search)
        )

    # ================= EDIT =================
    edit_id = request.GET.get("edit")
    edit_customer = get_object_or_404(Customer, id=edit_id) if edit_id else None

    return render(request, "admin/customer.html", {
        "customers": customers,
        "customer_types": TypeCustomer.objects.all(),
        "edit_customer": edit_customer,
        "search": search,
        "show_modal": True if edit_customer else False
    })

from ..models.user import Users
from ..models.employee import Employee
from ..models.role import Role
import re

def is_strong_password(password):
    if len(password) < 6:
        return False

    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[^a-zA-Z0-9]", password):
        return False

    return True

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from ..models import Users, Employee, Role


def admin_users(request):

    # ===== DELETE =====
    delete_id = request.GET.get("delete")
    if delete_id:
        Users.objects.filter(id=delete_id).delete()
        messages.success(request, "Đã xóa tài khoản")
        return redirect("adminpanel:admin_users")

    # ===== EDIT =====
    edit_user = None
    edit_id = request.GET.get("edit")
    if edit_id:
        edit_user = Users.objects.select_related("eid", "role").get(id=edit_id)

    # ===== ADD / UPDATE =====
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        email = request.POST.get("email", "").strip()
        eid = request.POST.get("eid")
        role_code = request.POST.get("role")

        if not all([username, email, eid, role_code]):
            messages.error(request, "Vui lòng nhập đầy đủ thông tin")
            return redirect(request.get_full_path())

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Email không đúng định dạng")
            return redirect(request.get_full_path())

        employee = Employee.objects.get(id=eid)
        role_obj = Role.objects.get(role=role_code)

        # ===== UPDATE =====
        if user_id:
            user = Users.objects.get(id=user_id)

            if Users.objects.filter(email=email).exclude(id=user_id).exists():
                messages.error(request, "Email đã được sử dụng")
                return redirect(request.get_full_path())

            user.email = email
            user.eid = employee
            user.role = role_obj

            if password:
                if not is_strong_password(password):
                    messages.error(
                        request,
                        "Mật khẩu phải ≥ 6 ký tự, gồm chữ hoa, chữ thường và ký tự đặc biệt"
                    )
                    return redirect(request.get_full_path())
                user.set_password(password)

            user.save()
            messages.success(request, "Cập nhật tài khoản thành công")
            return redirect("adminpanel:admin_users")

        # ===== ADD =====
        if Users.objects.filter(username=username).exists():
            messages.error(request, "Username đã tồn tại")
            return redirect(request.get_full_path())

        if Users.objects.filter(eid=employee).exists():
            messages.error(request, "Nhân viên này đã có tài khoản")
            return redirect(request.get_full_path())

        if Users.objects.filter(email=email).exists():
            messages.error(request, "Email đã được sử dụng")
            return redirect(request.get_full_path())

        if not password:
            messages.error(request, "Mật khẩu không được để trống")
            return redirect(request.get_full_path())

        if not is_strong_password(password):
            messages.error(
                request,
                "Mật khẩu phải ≥ 6 ký tự, gồm chữ hoa, chữ thường và ký tự đặc biệt"
            )
            return redirect(request.get_full_path())

        user = Users(
            username=username,
            email=email,
            eid=employee,
            role=role_obj,
            status="active"
        )
        user.set_password(password)
        user.save()

        messages.success(request, "Thêm tài khoản thành công")
        return redirect("adminpanel:admin_users")

    # ===== SEARCH =====
    keyword = request.GET.get("q", "").strip()
    users = Users.objects.select_related("eid", "role")

    if keyword:
        users = users.filter(
            Q(username__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(eid__name__icontains=keyword) |
            Q(eid__phone__icontains=keyword) |
            Q(role__role__icontains=keyword) |
            Q(role__role_name__icontains=keyword) |
            Q(status__icontains=keyword)
        )

    employees = Employee.objects.filter(user__isnull=True)
    if edit_user:
        employees = employees | Employee.objects.filter(id=edit_user.eid_id)

    return render(request, "admin/users.html", {
        "users": users,
        "employees": employees,
        "roles": Role.objects.all(),
        "keyword": keyword,
        "edit_user": edit_user,
        "show_modal": bool(edit_user)
    })



from myapp.models.customer_type import TypeCustomer


def admin_customer_type(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ===== THÊM / SỬA =====
    if request.method == "POST":
        cid = request.POST.get("id")          # có → sửa
        cid_new = request.POST.get("id_new")  # không có → thêm
        name = request.POST.get("name", "").strip()
        min_level = request.POST.get("minimumLevel")
        max_level = request.POST.get("maximumLevel")

        # ===== VALIDATE RỖNG =====
        if not name:
            messages.error(request, "Tên loại khách hàng không được để trống")
            return redirect("adminpanel:admin_customer_type")

        if not min_level or not max_level:
            messages.error(request, "Vui lòng nhập đầy đủ mức tối thiểu và tối đa")
            return redirect("adminpanel:admin_customer_type")

        try:
            min_level = int(min_level)
            max_level = int(max_level)
        except ValueError:
            messages.error(request, "Mức tối thiểu và tối đa phải là số")
            return redirect("adminpanel:admin_customer_type")

        if min_level > max_level:
            messages.error(request, "Mức tối thiểu không được lớn hơn mức tối đa")
            return redirect("adminpanel:admin_customer_type")

        # ===== VALIDATE THÊM =====
        if not cid:
            if not cid_new:
                messages.error(request, "Vui lòng nhập mã loại khách hàng")
                return redirect("adminpanel:admin_customer_type")

            if TypeCustomer.objects.filter(id=cid_new).exists():
                messages.error(request, "Mã loại khách hàng đã tồn tại")
                return redirect("adminpanel:admin_customer_type")

        # ===== VALIDATE TRÙNG TÊN =====
        if TypeCustomer.objects.filter(name=name).exclude(id=cid).exists():
            messages.error(request, "Tên loại khách hàng đã tồn tại")
            return redirect("adminpanel:admin_customer_type")

        # ===== SỬA =====
        if cid:
            TypeCustomer.objects.filter(id=cid).update(
                name=name,
                minimumLevel=min_level,
                maximumLevel=max_level
            )
            messages.success(request, "Cập nhật loại khách hàng thành công")

        # ===== THÊM =====
        else:
            TypeCustomer.objects.create(
                id=cid_new,
                name=name,
                minimumLevel=min_level,
                maximumLevel=max_level
            )
            messages.success(request, "Thêm loại khách hàng thành công")

        return redirect("adminpanel:admin_customer_type")

    # ===== XÓA =====
    delete_id = request.GET.get("delete")
    if delete_id:
        try:
            TypeCustomer.objects.get(id=delete_id).delete()
            messages.success(request, "Xóa loại khách hàng thành công")
        except TypeCustomer.DoesNotExist:
            messages.error(request, "Loại khách hàng không tồn tại")
        except:
            messages.error(request, "Không thể xóa loại khách hàng")
        return redirect("adminpanel:admin_customer_type")

    # ===== DANH SÁCH + TÌM KIẾM =====
    search = request.GET.get("search", "").strip()
    customer_types = TypeCustomer.objects.all()

    if search:
        customer_types = customer_types.filter(
            Q(id__icontains=search) |
            Q(name__icontains=search)
        )

    return render(request, "admin/customer_type.html", {
        "customer_types": customer_types,
        "search": search
    })


import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db import DataError
from myapp.models.manufacturer import Manufacturer
from myapp.models.department import Department
from myapp.models.position import Position


def generate_manufacturer_id():
    last_manu = Manufacturer.objects.filter(id__startswith="MANU").order_by("-id").first()
    if not last_manu:
        return "MANU001"

    match = re.search(r"MANU(\d+)", last_manu.id)
    number = int(match.group(1)) if match else 0
    return f"MANU{number + 1:03d}"


def admin_manufacturer(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ================= POST =================
    if request.method == "POST":
        eid = request.POST.get("id")
        name = request.POST.get("name", "").strip()
        country = request.POST.get("country", "").strip()


        errors = []

        # ===== VALIDATE NAME =====
        if not name:
            errors.append("Tên nhà sản xuất không được để trống")
        elif len(name) > 50:
            errors.append("Tên nahf sản xuất không được quá 50 ký tự")

        # ===== VALIDATE Country =====
        if not country:
            errors.append("Quốc gia không được để trống")
        
        
       
        else:
            country_qs = Manufacturer.objects.filter(country=country)
            if eid:
                country_qs = country_qs.exclude(id=eid)
            

        

        # ===== NẾU CÓ LỖI =====
        if errors:
            for e in errors:
                messages.error(request, e)

            return render(request, "admin/manufacturer.html", {
                "manufacturers": Manufacturer.objects.all(),
                "departments": Department.objects.all(),
                "positions": Position.objects.all(),
                "edit_manufacturer": get_object_or_404(Manufacturer, id=eid) if eid else None,
                "show_modal": True,
                "keyword": request.GET.get("q", "")
            })

        # ===== SAVE =====
        try:
            if eid:
                manufacturer = get_object_or_404(Manufacturer, id=eid)
                manufacturer.name = name
                manufacturer.country = country

                manufacturer.save()
                messages.success(request, "Cập nhật nhà sản xuất thành công")
            else:
                Manufacturer.objects.create(
                    id=generate_manufacturer_id(),
                    name=name,
                    country=country,
                    
                )
                messages.success(request, "Thêm nhà sản xuất thành công")

        except DataError:
            messages.error(request, "Dữ liệu không hợp lệ")
            return render(request, "admin/manufacturer.html", {
                "manufacturer": manufacturer.objects.select_related("did", "pid"),
                "departments": Department.objects.all(),
                "positions": Position.objects.all(),
                "edit_manufacturer": get_object_or_404(Manufacturer, id=eid) if eid else None,
                "show_modal": True,
                "keyword": ""
            })

        return redirect("adminpanel:admin_manufacturer")

    # ================= DELETE =================
    delete_id = request.GET.get("delete")
    if delete_id:
        Manufacturer.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa nhà sản xuất thành công")
        return redirect("adminpanel:admin_manufacturer")

    # ================= SEARCH =================
    keyword = request.GET.get("q", "").strip()
    manufacturers = Manufacturer.objects.all()


    if keyword:
        manufacturers = manufacturers.filter(
            Q(name__icontains=keyword) |
            Q(country__icontains=keyword)
        )


    edit_id = request.GET.get("edit")
    edit_manufacturer = get_object_or_404(Manufacturer, id=edit_id) if edit_id else None

    return render(request, "admin/manufacturer.html", {
        "manufacturers": manufacturers,        # <- đổi từ 'manufacturer' thành 'manufacturers'
        "departments": Department.objects.all(),
        "positions": Position.objects.all(),
        "edit_manufacturer": edit_manufacturer,  # <- fix typo
        "keyword": keyword,
        "show_modal": True if edit_manufacturer else False
    })

from django.http import JsonResponse

def ajax_find_customer(request):
    return JsonResponse({"status": "ok"})


from django.http import JsonResponse
from myapp.models import Customer

def ajax_find_customer(request):
    phone = request.GET.get("phone")
    try:
        c = Customer.objects.get(phone=phone)
        return JsonResponse({
            "exists": True,
            "id": c.id,
            "name": c.name,
            "phone": c.phone
        })
    except Customer.DoesNotExist:
        return JsonResponse({"exists": False})








from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from myapp.models import (
    Bill, BillDetails,
    Customer, Medicine,
    Users
)


# ==========================
# SINH MÃ HÓA ĐƠN TỰ ĐỘNG
# ==========================
def generate_bill_id():
    today = timezone.now().strftime('%Y%m%d')
    last_bill = Bill.objects.filter(
        id__startswith=f"HD{today}"
    ).order_by("-id").first()

    if last_bill:
        num = int(last_bill.id[-3:]) + 1
    else:
        num = 1

    return f"HD{today}{num:03d}"


# ==========================
# DANH SÁCH HÓA ĐƠN
# ==========================
def admin_bill(request):
    if not request.session.get("user_id"):
        return redirect("adminpanel:admin_login")

    bills = (
        Bill.objects
        .select_related("cid", "eid")
        .prefetch_related("details__mid")
        .order_by("-dateOfcreate")
    )

    return render(request, "admin/bill.html", {
        "bill": bills
    })


# ==========================
# TẠO HÓA ĐƠN (KHÔNG AJAX)
# ==========================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from myapp.models import Customer, Medicine, Bill, BillDetails


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from myapp.models import (
    Bill, BillDetails,
    Customer, Medicine,
    Users, TypeCustomer
)

def admin_bill_create(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    medicines = Medicine.objects.filter(quantity__gt=0)
    customer = None
    searched = False

    user = Users.objects.select_related("eid").get(
        id=request.session["user_id"]
    )
    employee = user.eid

    if request.method == "POST":
        action = request.POST.get("action")
        phone = request.POST.get("phone", "").strip()

        # ===== TÌM KHÁCH =====
        if action == "find":
            searched = True
            if phone:
                customer = Customer.objects.filter(
                    phone=phone,
                    is_active=True
                ).first()

        # ===== LƯU HÓA ĐƠN =====
        elif action == "save_bill":
            customer_id = request.POST.get("customer_id")

            if not customer_id:
                messages.error(request, "Vui lòng chọn khách hàng")
            else:
                customer = get_object_or_404(Customer, id=customer_id)

                try:
                    with transaction.atomic():
                        bill = Bill.objects.create(
                            id=generate_bill_id(),
                            cid=customer,
                            eid=employee,
                            totalAmount=0
                        )

                        total = 0
                        mids = request.POST.getlist("mid[]")
                        quantities = request.POST.getlist("quantity[]")

                        for mid, qty in zip(mids, quantities):
                            medicine = Medicine.objects.select_for_update().get(id=mid)
                            qty = int(qty)

                            if qty > medicine.quantity:
                                raise ValueError(
                                    f"Thuốc {medicine.name} không đủ tồn kho"
                                )

                            line_total = medicine.sellingPrice * qty
                            total += line_total

                            BillDetails.objects.create(
                                bid=bill,
                                mid=medicine,
                                quantity=qty,
                                unitPrice=medicine.sellingPrice,
                                totalAmount=line_total
                            )

                            medicine.quantity -= qty
                            medicine.save()

                        bill.totalAmount = total
                        bill.save()

                    messages.success(request, "Tạo hóa đơn thành công")
                    return redirect("adminpanel:admin_bill")

                except Exception as e:
                    messages.error(request, str(e))

    return render(request, "admin/bill_create.html", {
        "medicines": medicines,
        "customer": customer,
        "searched": searched
    })

def admin_customer_add_from_bill(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        name = request.POST.get("name", "").strip()
        address = request.POST.get("address", "")


        if not phone or not name:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin")
            return redirect(request.META.get("HTTP_REFERER"))

        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, "Số điện thoại đã tồn tại")
            return redirect(request.META.get("HTTP_REFERER"))

        # ===== LẤY LOẠI KHÁCH MẶC ĐỊNH =====
        try:
            normal_type = TypeCustomer.objects.get(id="TYP_CUS001")
        except TypeCustomer.DoesNotExist:
            messages.error(
                request,
                "Chưa cấu hình loại khách hàng mặc định (TYP_CUS001)"
            )
            return redirect(request.META.get("HTTP_REFERER"))

        Customer.objects.create(
            id=generate_customer_id(),
            name=name,
            phone=phone,
            address=address,
            tid=normal_type,          # <<< BẮT BUỘC
            totalExpenditure=0,
            cumulativePoints=0,
            is_active=True
        )

        messages.success(request, "Thêm khách hàng thành công")

    return redirect(request.META.get("HTTP_REFERER"))

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect
from weasyprint import HTML, CSS
from myapp.models import Bill
from django.conf import settings
import os


def admin_bill_pdf(request, bill_id):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    bill = Bill.objects.prefetch_related("details__mid").get(id=bill_id)

    html_string = render_to_string(
        "admin/bill_pdf.html",
        {"bill": bill}
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="bill_{bill.id}.pdf"'

    HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/")
    ).write_pdf(response)

    return response
