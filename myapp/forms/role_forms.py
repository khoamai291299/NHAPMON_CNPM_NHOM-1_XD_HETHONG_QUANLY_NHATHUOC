from django import forms
from myapp.models.role import Role

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role', 'role_name', 'status']

        widgets = {
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'role_name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(
                choices=[("active", "Đang hoạt động"), ("inactive", "Ngưng hoạt động")],
                attrs={'class': 'form-control'},
            ),
        }