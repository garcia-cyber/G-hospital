from django.contrib import admin
from .models import Fonction , Programme , TypeFonction , Patient

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
    list_display = ['fonction','user_fonction','statut_fonction']

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
    list_display = ['id','noms','sexe','age','adresse','poids','dateEn']
    search_fields = ['noms',]