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
        fields = ['noms','sexe','age','adresse','poids','service_patient','commune'] 
        widgets = {
            'noms': forms.TextInput(attrs={'class':'form-control'}) ,
            'sexe' : forms.Select(attrs={'class':'form-control'}) ,
            'age'  : forms.NumberInput(attrs={'class':'form-control'}) ,
            'commune' : forms.Select(attrs={'class':'form-control'}) ,
            'adresse': forms.TextInput(attrs={'class':'form-control'}) ,
            'poids' : forms.NumberInput(attrs={'class':'form-control'}) , 
            'service_patient' : forms.Select(attrs={'class':'form-control'}) ,
        }

    def __init__(self , *args , **kwargs):
        super(PatientForm,self).__init__(*args,**kwargs)
        self.fields['service_patient'].queryset = Service.objects.filter(service__in = ['pediatrie','gyneco'])




# =============================================
# prestation formulaire
# =============================================




class EncaissementGlobalForm(forms.ModelForm):
    prestation = forms.ModelChoiceField(
        queryset=Prestation.objects.all(),
        label="Sélectionner la prestation",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Paiement
        fields = ['montant_verse']
        widgets = {
            'montant_verse': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant versé'})
        }

    def clean(self):
        cleaned_data = super().clean()
        prestation_choisie = cleaned_data.get('prestation')
        montant_donne = cleaned_data.get('montant_verse')

        # Nous n'avons pas accès au patient ici facilement, 
        # donc on garde une validation de base sur le prix total.
        if prestation_choisie and montant_donne:
            prix_total = prestation_choisie.prix_fixe

            # 1. Empêcher de donner plus que le prix de base de la prestation
            if montant_donne > prix_total:
                raise forms.ValidationError(
                    f"Erreur : Le montant saisi ({montant_donne} CDF) est supérieur au prix de la prestation ({prix_total} CDF)."
                )
            
            # 2. Empêcher de saisir 0 ou un montant négatif
            if montant_donne <= 0:
                raise forms.ValidationError("Le montant versé doit être supérieur à 0.")
        
        return cleaned_data
    


    


# ===========================================
# On ajoute le choix de la prestation dans le formulaire
# ===================================

# class EncaissementForm(forms.ModelForm):
#     # On ajoute le choix de la prestation dans le formulaire
#     prestation = forms.ModelChoiceField(queryset=Prestation.objects.all())

#     class Meta:
#         model = Paiement
#         fields = ['montant_verse']



# ==============================================
# nouveau dossier pour mon formulaire facture 
# ===============================================
# class EncaissementInitialForm(forms.Form):
#     prestation = forms.ModelChoiceField(
#         queryset=Prestation.objects.all(),
#         widget=forms.Select(attrs={'class': 'form-control select2'})
#     )
#     montant_verse = forms.DecimalField(
#         max_digits=10, 
#         decimal_places=2,
#         widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant à payer...'})
#     )

class EncaissementForm(forms.Form):
    # On laisse required=False pour la prestation car si on paie une dette existante, 
    # la prestation est déjà connue dans la facture.
    prestation = forms.ModelChoiceField(
        queryset=Prestation.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    montant_verse = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )