from django.urls import path  
from .views import login , panel , deco , encaisser_prestation
from .views import * 


urlpatterns = [
    path('login/', login , name='login') , 
    path('panel/', panel , name = 'panel') , 
    path('deco/', deco , name='deco'),
    path('typeFonctionAdd/', type_fonction_add , name='type_fonction_add') , 
    path('employeAdd', employeAdd , name = 'employeAdd') , 
    path('employeRead', employeRead , name='employeRead') , 
    path('employeUpdate/<int:id>', employeUpdate , name='employeUpdate') , 
    path('patientAdd/', patientAdd , name="patientAdd") , 
    path('patientRead/', patientRead , name ="patientRead") , 
    path('', home , name= 'home') , 
    path('employeProfil/<int:user_id>/', employeProfil , name= 'employeProfil') ,
    path('profilRead/', profilRead , name='profilRead') , 
    path('historique/<int:patient_id>/', liste_factures_patient, name='liste_factures_patient'),
    path('imprimer-recu/<int:facture_id>/', imprimer_recu, name='imprimer_recu'),
    path('patient/<int:patient_id>/nouveau-paiement/', encaisser_prestation, name='nouveau_paiement'),
    path('facture/<int:facture_id>/encaisser/', encaisser_prestation, name='encaisser_prestation'),
    path('imprimer-tranche/<int:paiement_id>/', imprimer_recu_tranche, name='imprimer_recu_tranche'),
    path('imprimer-facture-globale/<int:facture_id>/', imprimer_recu, name='imprimer_recu'),
]
