from django import forms 
from .models import TypeFonction 


# creaation du formulaire d'authentification 
# ==========================================
# ==========================================
class LoginForm(forms.Form):
    username = forms.CharField(max_length = 30 , widget = forms.TextInput(attrs={'class':'form-control'})) 
    password = forms.CharField(max_length = 200 , widget = forms.PasswordInput(attrs={'class':'form-control'})) 


# creaation du formulaire de type de fonction  
# ===========================================
# ===========================================
class TypeFonctionForm(forms.ModelForm):
    class Meta :
        model = TypeFonction
        fields = ['type_fonction'] 
        widgets = {
            'type_fonction': forms.TextInput(attrs={'class': 'form-control'})
        }