from django import forms
from myapp.models.medicine_type import TypeMedicine

class TypeMedicineForm(forms.ModelForm):
    class Meta:
        model = TypeMedicine
        fields = ['id', 'name', 'description']
        widgets = {
            'id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
