from django import forms 
from .models import TypeFonction , Patient
from django.contrib.auth.models import User
from .models import * 


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

# ====================================================
# profil employes 
# ====================================================
class ProfilAddForm(forms.ModelForm):
    class Meta:
        model = Fonction 
        fields = ['fonction','service','etatCivil','phone','adresse','commune'] 
        widgets = {
            'fonction': forms.Select(attrs={'class':'form-control'}) ,
            'service' : forms.Select(attrs={'class':'form-control'}) , 
            'etatCivil' : forms.Select(attrs={'class':'form-control'}) , 
            'phone'     : forms.NumberInput(attrs={'class':'form-control'}) ,
            'adresse'   : forms.TextInput(attrs={'class':'form-control'}) ,
            'commune'   : forms.Select(attrs={'class':'form-control'}) , 
        }

# ====================================================
# patient form 
# ====================================================
class PatientForm(forms.ModelForm):
    class Meta :
        model = Patient 
        fields = ['noms','sexe','age','adresse','poids'] 
        widgets = {
            'noms': forms.TextInput(attrs={'class':'form-control'}) ,
            'sexe' : forms.Select(attrs={'class':'form-control'}) ,
            'age'  : forms.NumberInput(attrs={'class':'form-control'}) ,
            'adresse': forms.TextInput(attrs={'class':'form-control'}) ,
            'poids' : forms.NumberInput(attrs={'class':'form-control'})
        }