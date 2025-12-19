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
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

def generate_employee_id():
    """
    Sinh mã nhân viên dạng: EMP001, EMP002, ...
    """
    last_emp = Employee.objects.filter(id__startswith="EMP").order_by("-id").first()

    if not last_emp:
        return "EMP001"

    match = re.search(r"EMP(\d+)", last_emp.id)
    number = int(match.group(1)) if match else 0

    return f"EMP{number + 1:03d}"
from django.shortcuts import get_object_or_404

def admin_employee(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ===== POST: THÊM / SỬA =====
    if request.method == "POST":
        eid = request.POST.get("id")  # có id → sửa, không có → thêm
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        sex = request.POST.get("sex")
        salary = request.POST.get("salary")
        did = request.POST.get("did")
        pid = request.POST.get("pid")

        if not name or not phone or not salary or not did or not pid:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin")
            return redirect("adminpanel:admin_employee")

        # ===== CHECK TRÙNG SĐT =====
        phone_qs = Employee.objects.filter(phone=phone)
        if eid:                       # nếu sửa → loại trừ chính nó
            phone_qs = phone_qs.exclude(id=eid)

        if phone_qs.exists():
            messages.error(request, "Số điện thoại đã tồn tại")
            return redirect("adminpanel:admin_employee")

        # ===== SỬA =====
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

        # ===== THÊM =====
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

        return redirect("adminpanel:admin_employee")

    # ===== XÓA =====
    delete_id = request.GET.get("delete")
    if delete_id:
        Employee.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa nhân viên thành công")
        return redirect("adminpanel:admin_employee")

    employees = Employee.objects.select_related("did", "pid")
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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q

from myapp.models.medicine import Medicine
from myapp.models.medicine_type import TypeMedicine
from myapp.models.manufacturer import Manufacturer


def admin_product(request):
    # =========================
    # KIỂM TRA ĐĂNG NHẬP
    # =========================
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # =========================
    # THÊM / SỬA
    # =========================
    if request.method == "POST":
        medicine_id = request.POST.get("id")       # dùng khi sửa
        new_id = request.POST.get("id_new")        # dùng khi thêm

        try:
            data = {
                "name": request.POST.get("name", "").strip(),
                "productionDate": request.POST.get("productionDate") or None,
                "expirationDate": request.POST.get("expirationDate") or None,
                "unit": request.POST.get("unit", "").strip(),
                "quantity": int(request.POST.get("quantity") or 0),
                "importPrice": int(request.POST.get("importPrice") or 0),
                "sellingPrice": int(request.POST.get("sellingPrice") or 0),
                "tid_id": request.POST.get("tid"),
                "mid_id": request.POST.get("mid"),
            }
        except ValueError:
            messages.error(request, "Số lượng hoặc giá không hợp lệ")
            return redirect("adminpanel:admin_product")

        # ===== VALIDATE =====
        if not data["name"]:
            messages.error(request, "Tên thuốc không được để trống")
            return redirect("adminpanel:admin_product")

        # =========================
        # SỬA THUỐC
        # =========================
        if medicine_id:
            Medicine.objects.filter(id=medicine_id).update(**data)
            messages.success(request, "Cập nhật thuốc thành công")

        # =========================
        # THÊM THUỐC
        # =========================
        else:
            if not new_id:
                messages.error(request, "Mã thuốc không được để trống")
                return redirect("adminpanel:admin_product")

            # check trùng mã
            if Medicine.objects.filter(id=new_id).exists():
                messages.error(request, "Mã thuốc đã tồn tại")
                return redirect("adminpanel:admin_product")

            Medicine.objects.create(
                id=new_id,     # 🔥 BẮT BUỘC
                **data
            )
            messages.success(request, "Thêm thuốc thành công")

        return redirect("adminpanel:admin_product")

    # =========================
    # XÓA
    # =========================
    delete_id = request.GET.get("delete")
    if delete_id:
        Medicine.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa thuốc thành công")
        return redirect("adminpanel:admin_product")

    # =========================
    # TÌM KIẾM
    # =========================
    search = request.GET.get("search", "").strip()

    medicines = Medicine.objects.select_related("tid", "mid")

    if search:
        medicines = medicines.filter(
            Q(id__icontains=search) |
            Q(name__icontains=search) |
            Q(tid__name__icontains=search) |
            Q(mid__name__icontains=search)
        )

    # =========================
    # HIỂN THỊ
    # =========================
    return render(request, "admin/product.html", {
        "medicines": medicines,
        "search": search,
        "types": TypeMedicine.objects.all(),
        "manufacturers": Manufacturer.objects.all(),
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
        edit_user = Users.objects.get(id=edit_id)

    # ===== ADD / UPDATE =====
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        email = request.POST.get("email", "").strip()
        eid = request.POST.get("eid")
        role_id = request.POST.get("role")

        if not all([username, email, eid, role_id]):
            messages.error(request, "Vui lòng nhập đầy đủ thông tin")
            return redirect(request.get_full_path())

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Email không đúng định dạng")
            return redirect(request.get_full_path())

        employee = Employee.objects.get(id=eid)

        # ===== UPDATE =====
        if user_id:
            
            user = Users.objects.get(id=user_id)
            user.email = email
            user.eid = employee
            user.role_id = role_id
            if Users.objects.filter(email=email).exclude(id=user_id).exists():
                messages.error(request, "Email đã được sử dụng")
                return redirect(request.get_full_path())
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

        if Users.objects.filter(eid_id=eid).exists():
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
            role_id=role_id,
            status="active"
        )
        user.set_password(password)
        user.save()

        messages.success(request, "Thêm tài khoản thành công")
        return redirect("adminpanel:admin_users")

    # ===== SEARCH + RENDER (BẮT BUỘC CÓ RETURN) =====
    
    keyword = request.GET.get("q", "").strip()
    users = Users.objects.select_related("eid")

    if keyword:
        users = users.filter(
            Q(username__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(eid__name__icontains=keyword) |
            Q(eid__phone__icontains=keyword) |
            Q(role_id__icontains=keyword) |
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


from django.db.models import Q
from myapp.models.manufacturer import Manufacturer
from django.contrib import messages

def admin_manufacturer(request):
    if 'user_id' not in request.session:
        return redirect('adminpanel:admin_login')

    # ===== THÊM / SỬA =====
    if request.method == "POST":
        mid = request.POST.get("id")
        mid_new = request.POST.get("id_new")
        name = request.POST.get("name", "").strip()
        country = request.POST.get("country", "").strip()

        if not mid and Manufacturer.objects.filter(id=mid_new).exists():
            messages.error(request, "Mã nhà sản xuất đã tồn tại")
            return redirect("adminpanel:admin_manufacturer")

        if Manufacturer.objects.filter(name=name).exclude(id=mid).exists():
            messages.error(request, "Tên nhà sản xuất đã tồn tại")
            return redirect("adminpanel:admin_manufacturer")

        if mid:
            Manufacturer.objects.filter(id=mid).update(
                name=name,
                country=country
            )
            messages.success(request, "Cập nhật nhà sản xuất thành công")
        else:
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
        Manufacturer.objects.filter(id=delete_id).delete()
        messages.success(request, "Xóa nhà sản xuất thành công")
        return redirect("adminpanel:admin_manufacturer")

    # ===== TÌM KIẾM =====
    search = request.GET.get("search", "").strip()

    manufacturers = Manufacturer.objects.all()
    if search:
        manufacturers = manufacturers.filter(
            Q(id__icontains=search) |
            Q(name__icontains=search) |
            Q(country__icontains=search)
        )

    return render(request, "admin/manufacturer.html", {
        "manufacturer": manufacturers,
        "search": search
    })
