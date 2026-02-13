from django import forms 
from .models import TypeFonction 
from django.contrib.auth.models import User


# creation du formulaire d'authentification 
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

# ===========================================
# employes add   
# ===========================================

class EmployeForm(forms.ModelForm):
    password = forms.CharField(max_length=200 , widget= forms.PasswordInput(attrs={'class':'form-control'}), label='mot de passe utilisateur') 

    class  Meta:
        model = User 
        fields = ['username','email','password']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}) ,
            'email': forms.EmailInput(attrs={'class':'form-control'}) ,
            
        }      

        labels = {
            'username': 'nom utilisateur' , 
            'email': 'email utilisateur' , 
            'password': 'mot de passe utilisateur' , 

        }  

# ===================================================
# mise en jour employe 
# ===================================================
class EmployeUpdateForm(forms.ModelForm):
    class Meta :
        model = User 
        fields = ['username', 'email'] 
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}) ,
            'email': forms.EmailInput(attrs={'class':'form-control'}) ,

        }