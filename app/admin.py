from django.contrib import admin
from .models import Fonction , Programme , TypeFonction , Patient 
from .models import *

# Register your models here.

## ======================================
## ======================================
##
## type de fonction 
@admin.register(TypeFonction)
class TypeFonctionAdmin(admin.ModelAdmin):
    list_display = ['type_fonction'] 

## ====================================
## ====================================
## 
##  fonction 
@admin.register(Fonction)
class FonctionAdmin(admin.ModelAdmin):
    list_display = ['fonction','user_fonction','statut_fonction','service','commune','adresse','phone','etatCivil']

## ====================================
## ====================================
##
## programme 
@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin) :
    list_display = ['statutProgramme','dateProgramme']

# ===============================================
# models patient 
# ===============================================
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id','noms','sexe','age','adresse','poids','dateEn','userPatient','service_patient','userPatient__email']
    search_fields = ['noms',]

# ==============================================
# models communes
# =============================================
@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ['nomCommune'] 


# ==============================================
# models stagiaires
# ==============================================
@admin.register(Stagiare)
class StagiaireAdmin(admin.ModelAdmin):
    list_display = ['nomStagiaires','sexe','phone','commune','adresse','type_stage','dateDebut','dateFin','userStagiaire__username'] 
    search_fields = ['nomStagiaires' , 'type_stage',]

# ===============================================
# service 
# ===============================================
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display =['service']
    search_fields = ['service',] 


# ===========================================
# prestation 
# ==========================================
@admin.register(Prestation)
class PrestationAdmin(admin.ModelAdmin):
    list_display = ['libelle','prix_fixe']

# ============================================
# facture 
# ============================================
@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['patient','prestation','total_a_payer','date_emission','est_soldee']

# =========================================
# Consultation
# =========================================
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient','service','facture','temperature','poids','tension','statut', 'date_creation']