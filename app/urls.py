from django.urls import path  
from .views import login , panel , deco , encaisser_prestation
from .views import * 
from . import views


urlpatterns = [
    # Authentification & Dashboard
    path('login/', views.login , name='login') , 
    path('panel/', views.panel , name = 'panel') , 
    path('deco/', views.deco , name='deco'),
    path('', views.home , name= 'home') , 

    # Gestion du Personnel & Fonctions
    path('typeFonctionAdd/', views.type_fonction_add , name='type_fonction_add') , 
    path('employeAdd/', views.employeAdd , name = 'employeAdd') , 
    path('employeRead/', views.employeRead , name='employeRead') , 
    path('employeUpdate/<int:id>/', views.employeUpdate , name='employeUpdate') , 
    path('employeProfil/<int:user_id>/', views.employeProfil , name= 'employeProfil') ,
    path('profilRead/', views.profilRead , name='profilRead') , 

    # Gestion des Patients
    path('patientAdd/', views.patientAdd , name="patientAdd") , 
    path('patientRead/', views.patientRead , name ="patientRead") , 

    # Facturation & Paiements
    path('historique/<int:patient_id>/', views.liste_factures_patient, name='liste_factures_patient'),
    path('imprimer-recu/<int:facture_id>/', views.imprimer_recu, name='imprimer_recu'),
    path('patient/<int:patient_id>/nouveau-paiement/', views.encaisser_prestation, name='nouveau_paiement'),
    path('facture/<int:facture_id>/encaisser/', views.encaisser_prestation, name='encaisser_prestation'),
    path('imprimer-tranche/<int:paiement_id>/', views.imprimer_recu_tranche, name='imprimer_recu_tranche'),
    path('imprimer-facture-globale/<int:facture_id>/', views.imprimer_recu, name='imprimer_recu'),

    # --- NOUVEAU : Catalogue des Prestations (Tarification) ---
    path('prestation/liste/', views.prestation_list, name='prestation_list'),
    path('prestation/ajouter/', views.prestation_add, name='prestation_add'),
    path('prestation/modifier/<int:pk>/', views.prestation_edit, name='prestation_edit'),

    # Consultation & Médical
    path('prelever-signes/<int:consultation_id>/', views.prelever_signes, name='prelever_signes'),
    path('consultation/<int:consultation_id>/', views.faire_consultation, name='faire_consultation'),

    path('caisse/payer/<int:consultation_id>/', views.encaisser_examen, name='encaisser_examen'),

    path('encaisser-tranche/<int:facture_id>/', views.ajouter_tranche, name='ajouter_tranche'),

    # Page principale des documents (Affichage + Ajout)
    path('documents/', views.gestion_documents, name='gestion_documents'),
    
    # Action de suppression (L'ID est passé dans l'URL)
    path('documents/supprimer/<int:doc_id>/', views.supprimer_document, name='supprimer_document'),
    path('consultation/creer/<int:facture_id>/', views.creer_consultation, name='creer_consultation'),
    path('triage/prelever/<int:consultation_id>/', views.prelever_signes, name='prelever_signes'),

    # Présence & Pointage
    path('reception/presence/', views.tableau_presence_reception, name='presence_reception'),
    path('reception/pointage/<int:user_id>/', views.pointer_employe, name='marquer_pointage'),
    path('reception/archives/', views.historique_presences, name='historique_presence'),
    path('presence/statistiques/', views.statistiques_presence, name='statistiques_presence'),
    path('presence/pdf/', views.generer_pdf_presence, name='generer_pdf_presence'),

    # Stock & Matériel
    path('materiel/ajouter/', views.ajouter_materiel, name='ajouter_materiel'),
    path('materiel/liste/', views.liste_materiel, name='liste_materiel'),
    path('materiel/categories/', views.gestion_categories, name='gestion_categories'),
]
