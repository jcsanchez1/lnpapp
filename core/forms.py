from django import forms
from .models import Expediente
class ExpedienteForm(forms.ModelForm):
   class Meta:
       model = Expediente
       fields = ['dni', 'nombre', 'apellido', 'sexo']

class ExpedienteSearchForm(forms.Form):
    dni = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese DNI'})
    )

class ExpedienteForm(forms.ModelForm):
    crear_muestra = forms.BooleanField(required=False, label='Crear muestra después')
    
    class Meta:
        model = Expediente
        fields = ['dni', 'nombre', 'apellido', 'sexo']
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'})
        }