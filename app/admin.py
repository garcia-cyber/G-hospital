from django.contrib import admin
from .models import (
    Service, TypeFonction, Fonction, Patient, 
    Prestation, Facture, Paiement, Consultation, 
    Commune, Notification, Programme, Presence, Conge
)
from .models import * 

# 1. Configuration pour le Service
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
    search_fields = ('nom',)

# 2. Configuration pour le Patient
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('noms', 'sexe', 'age', 'phone_responsable', 'dateEn')
    search_fields = ('noms', 'phone_responsable')
    list_filter = ('sexe', 'commune', 'service_patient')

# 3. Configuration pour les Prestations
@admin.register(Prestation)
class PrestationAdmin(admin.ModelAdmin):
    # Correction : Utilisation de 'nom_prestation' ou 'libelle' selon ton modèle
    list_display = ('id', 'prix_fixe', 'service') 
    list_filter = ('service',)

# 4. Configuration pour les Factures
@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    # Ajout de 'consultation' pour voir le lien avec les examens du médecin
    list_display = ('id', 'afficher_patient', 'consultation', 'total_a_payer', 'date_emission', 'est_soldee')
    list_filter = ('date_emission',)
    readonly_fields = ('date_emission',)

    def afficher_patient(self, obj):
        return obj.patient.noms
    afficher_patient.short_description = 'Patient'

# 5. Configuration pour les Paiements (CORRIGÉ : mode_paiement supprimé)
@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    # Suppression de 'mode_paiement' pour éviter l'erreur SystemCheckError
    list_display = ('id', 'facture', 'afficher_patient', 'montant_verse', 'date_paiement', 'recepteur')
    list_filter = ('date_paiement', 'recepteur')

    def afficher_patient(self, obj):
        return obj.facture.patient.noms
    afficher_patient.short_description = 'Nom du Patient'

# 6. Configuration pour les Consultations
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    # Ajout de total_a_payer_examens pour surveiller les 150.000 FC
    list_display = ('id', 'patient', 'statut', 'total_a_payer_examens', 'reste_a_payer', 'date_creation')
    list_filter = ('statut', 'service')
    search_fields = ('patient__noms',)

# 7. Configuration pour le Personnel
@admin.register(Fonction)
class FonctionAdmin(admin.ModelAdmin):
    list_display = ('user_fonction', 'fonction', 'service', 'statut_fonction', 'phone')
    list_filter = ('statut_fonction', 'service')
    search_fields = ('user_fonction__username', 'phone')

# 8. Autres modèles
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'titre', 'date_envoi', 'est_lu')
    list_filter = ('est_lu',)

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('id', 'statutProgramme', 'dateProgramme')

admin.site.register(TypeFonction)
admin.site.register(Commune)

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'date', 'heure_arrivee', 'heure_depart', 'enregistre_par')
    list_filter = ('date', 'employe')
    search_fields = ('employe__username', 'employe__first_name', 'employe__last_name')
    ordering = ('-date',)

    def get_full_name(self, obj):
        return obj.employe.get_full_name() or obj.employe.username
    get_full_name.short_description = 'Employé'

@admin.register(Conge)
class CongeAdmin(admin.ModelAdmin):
    list_display = ('employe', 'type_conge', 'date_debut', 'date_fin', 'statut')
    list_filter = ('statut', 'type_conge', 'date_debut')
    search_fields = ('employe__username', 'motif')
    list_editable = ('statut',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('date_heure', 'agent', 'source', 'montant', 'ref_objet')
    
    # Filtres latéraux (très utile pour la comptabilité)
    list_filter = ('source', 'date_heure', 'agent')
    
    # Barre de recherche (recherche par nom d'utilisateur ou ID de référence)
    search_fields = ('agent__username', 'ref_objet')
    
    # Tri par défaut (les plus récentes en premier)
    ordering = ('-date_heure',)
    
    # Rendre certains champs en lecture seule pour éviter les fraudes accidentelles
    readonly_fields = ('date_heure',)

# --- 1. Gestion des Documents ---
@admin.register(DocumentHospitalier)
class DocumentHospitalierAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_document', 'patient', 'date_creation', 'ajoute_par', 'apercu_fichier')
    list_filter = ('type_document', 'date_creation', 'ajoute_par')
    search_fields = ('titre', 'patient__noms', 'ajoute_par__username')
    readonly_fields = ('date_creation',)
    autocomplete_fields = ['patient'] # Nécessite search_fields dans PatientAdmin

    def apercu_fichier(self, obj):
        if obj.fichier:
            ext = obj.extension[1] # Récupère l'extension via ta propriété
            if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                return format_html('<img src="{}" style="width: 45px; height:45px; border-radius:5px;" />', obj.fichier.url)
            return format_html('<a href="{}" target="_blank"><i class="fas fa-file-download"></i> Voir le fichier</a>', obj.fichier.url)
        return "Aucun fichier"
    apercu_fichier.short_description = "Aperçu / Lien"

# --- 2. Gestion du Matériel (Stock) ---
@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):
    list_display = ('designation', 'categorie', 'stock_visuel', 'seuil_alerte', 'unite_mesure')
    list_filter = ('categorie', 'unite_mesure')
    search_fields = ('designation',)
    list_editable = ('seuil_alerte',) # Permet de modifier le seuil sans ouvrir la fiche

    def stock_visuel(self, obj):
        # Indicateur de couleur selon le niveau de stock
        color = "green"
        if obj.quantite_stock <= 0:
            color = "red"
        elif obj.quantite_stock <= obj.seuil_alerte:
            color = "orange"
        
        return format_html(
            '<b style="color: {}; font-size: 14px;">{} {}</b>',
            color, obj.quantite_stock, obj.unite_mesure
        )
    stock_visuel.short_description = "État du Stock"

# --- 3. Gestion des Mouvements de Stock ---
@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('date_mouvement', 'materiel', 'type_badge', 'quantite_formattee')
    list_filter = ('type_mouvement', 'date_mouvement', 'materiel__categorie')
    search_fields = ('materiel__designation', 'description')
    date_hierarchy = 'date_mouvement' # Barre de navigation temporelle en haut

    def type_badge(self, obj):
        colors = {'ENTREE': '#28a745', 'SORTIE': '#dc3545'}
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold;">{}</span>',
            colors.get(obj.type_mouvement, 'grey'),
            obj.get_type_mouvement_display()
        )
    type_badge.short_description = "Type"

    def quantite_formattee(self, obj):
        prefix = "+" if obj.type_mouvement == 'ENTREE' else "-"
        return f"{prefix}{obj.quantite}"
    quantite_formattee.short_description = "Quantité"

# --- 4. Catégorie (Optionnel mais nécessaire pour Materiel) ---
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)