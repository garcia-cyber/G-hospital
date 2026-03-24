from django import forms
from django.contrib.auth.models import User
from .models import (
    TypeFonction, Patient, Fonction, Service, 
    Prestation, Paiement, Commune
)
from .models import *
from django.core.exceptions import ValidationError

# 1. Formulaire d'authentification
# ==========================================
class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control'})) 
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class':'form-control'})) 

# 2. Formulaire Type de Fonction
# ===========================================
class TypeFonctionForm(forms.ModelForm):
    class Meta:
        model = TypeFonction
        fields = ['type_fonction'] 
        widgets = {
            'type_fonction': forms.TextInput(attrs={'class': 'form-control'})
        }

# 3. Formulaire Ajout Employé (User)
# ===========================================
class EmployeForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe utilisateur"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: gracia'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@g-hospital.cd'}),
        }
        labels = {
            'username': 'Nom utilisateur',
            'email': 'Email utilisateur',
        }

    # MÉTHODE DE VALIDATION PERSONNALISÉE
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # On vérifie si un utilisateur avec ce nom existe déjà (insensible à la casse)
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(f"L'identifiant '{username}' est déjà utilisé par un autre employé.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
# 4. Mise à jour Employé
# ===========================================
class EmployeUpdateForm(forms.ModelForm):
    class Meta:
        model = User 
        fields = ['username', 'email'] 
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
        }

# 5. Profil Employé (CORRIGÉ : Retrait de 'commune')
# ===========================================
class ProfilAddForm(forms.ModelForm):
    class Meta:
        model = Fonction 
        # 'commune' est retiré car absent du modèle Fonction
        fields = ['fonction', 'service', 'etatCivil', 'phone', 'adresse'] 
        widgets = {
            'fonction': forms.Select(attrs={'class':'form-control'}),
            'service' : forms.Select(attrs={'class':'form-control'}), 
            'etatCivil' : forms.Select(attrs={'class':'form-control'}), 
            'phone'     : forms.TextInput(attrs={'class':'form-control'}), # Changé en TextInput pour la flexibilité
            'adresse'   : forms.TextInput(attrs={'class':'form-control'}),
        }

# 6. Formulaire Patient
# ===========================================
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient 
        fields = ['noms', 'sexe', 'age', 'phone_responsable','adresse', 'poids', 'service_patient', 'commune']
        widgets = {
            'noms': forms.TextInput(attrs={'class':'form-control'}),
            'sexe' : forms.Select(attrs={'class':'form-control'}),
            'age'  : forms.NumberInput(attrs={'class':'form-control'}),
            'commune' : forms.Select(attrs={'class':'form-control'}),
            'adresse': forms.TextInput(attrs={'class':'form-control'}),
            'poids' : forms.NumberInput(attrs={'class':'form-control'}), 
            'service_patient' : forms.Select(attrs={'class':'form-control'}),
            'phone_responsable' : forms.NumberInput(attrs ={'class':'form-control'})
        }

        labels = {
            'noms' : 'noms du patient'
        }

    def __init__(self,*args , **kwargs):
        super(PatientForm,self).__init__(*args , **kwargs)
        self.fields['service_patient'].queryset = Service.objects.filter(nom__in = ['gyneco','pediatrie' , 'maternite','medecin interne'])




# 7. Formulaire Encaissement Global
# ===========================================
class EncaissementGlobalForm(forms.ModelForm):
    prestation = forms.ModelChoiceField(
        queryset=Prestation.objects.filter(active=True, est_fiche_obligatoire=True),
        label="Type de Fiche",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_prestation'})
    )

    class Meta:
        model = Paiement
        fields = ['montant_verse', 'prestation']
        widgets = {
            'montant_verse': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg text-center font-weight-bold',
                'id': 'id_montant_verse',
                'step': '0.01'
            })
        }

    def __init__(self, *args, **kwargs):
        self.facture = kwargs.pop('facture', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        montant = cleaned_data.get('montant_verse')
        prestation = cleaned_data.get('prestation')

        if montant and prestation:
            # CAS 1 : C'est une nouvelle facture (Premier paiement)
            if not self.facture:
                prix_max = prestation.prix_fixe
                if montant > prix_max:
                    raise forms.ValidationError(
                        f"Erreur : Le prix de la prestation '{prestation.nom}' est de {prix_max} FC. "
                        f"Vous ne pouvez pas encaisser {montant} FC."
                    )
            
            # CAS 2 : C'est un paiement pour une facture existante (Tranche)
            else:
                reste = self.facture.reste_a_payer
                if montant > reste:
                    raise forms.ValidationError(
                        f"Erreur : Le reste à payer pour cette facture est de {reste} FC. "
                        f"Le montant versé ({montant} FC) est trop élevé."
                    )

        return cleaned_data
# 8. Formulaire Encaissement (Vue Facture)
# ===========================================
class EncaissementForm(forms.Form):
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



# 9. prestation 
# ===============================================
class PrestationForm(forms.ModelForm):
    class Meta:
        model = Prestation
        # fields = ['libelle', 'prix_fixe', 'service', 'type_prestation', 'est_fiche_obligatoire', 'active']
        fields = ['libelle', 'prix_fixe','type_prestation', 'est_fiche_obligatoire', 'active']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Consultation Générale'}),
            'prix_fixe': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en FC'}),
            # 'service': forms.Select(attrs={'class': 'form-control select2'}),
            'type_prestation': forms.Select(attrs={'class': 'form-control'}),
            # Note : Pour les checkbox, 'custom-control-input' demande souvent un container <div> spécifique en HTML
            'est_fiche_obligatoire': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'active': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }

    def __init__(self, *args, **kwargs):
        # CORRECTION 1 : On utilise PrestationForm ici, PAS PatientForm
        super(PrestationForm, self).__init__(*args, **kwargs)
        
        # CORRECTION 2 : Le champ s'appelle 'service' dans ton modèle Prestation (pas service_patient)
        # On s'assure que le champ existe avant de le filtrer pour éviter d'autres erreurs
        # if 'service' in self.fields:
        #     self.fields['service'].queryset = Service.objects.all() 
            # Si tu veux filtrer spécifiquement :
            # self.fields['service'].queryset = Service.objects.filter(nom__icontains='pediatrie')