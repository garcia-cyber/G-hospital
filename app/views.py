from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth import authenticate , login as auth , logout 
from django.contrib.auth.decorators import login_required 
from .forms import LoginForm , TypeFonctionForm ,EmployeForm , EmployeUpdateForm  , PatientForm 
from .models import Fonction
from django.contrib.auth.models import User
from .models import * 
from .forms import  *
import qrcode
from django.utils import timezone
import qrcode.image.svg
from io import BytesIO
from django.contrib import messages # N'oubliez pas cet import tout en haut
from django.db.models import Q
from datetime import datetime
from django.utils.dateparse import parse_date
from django.http import HttpResponse  # <-- AJOUTE CETTE LIGNE ICI
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import date
from django.core.paginator import Paginator

# Create your views here.


def home(request):
    return render(request , 'front/index.html')


#==============================================================
# login 
# =============================================================
def login(request):
    msg = None
    if request.method == 'POST':
        form = LoginForm(request.POST) 
        if form.is_valid():
            username = form.cleaned_data['username'] 
            password = form.cleaned_data['password'] 

            user = authenticate(username = username , password = password) 
            if user :
                auth(request,user) 
                return redirect('panel') 
            else:
                msg = "mot de passe erronne !!!:🤞"
    form = LoginForm()
    return render(request, 'back/auth-login.html', {'form':form , 'msg':msg})  

# =============================================================
# deconnexion 
# ============================================================
def deco(request):
    logout(request)
    return redirect('home')

# ============================================================
# PANEL DE CONTROLE (CORRIGÉ POUR TA LOGIQUE)
# =============================================================
@login_required()
def panel(request):
    myUser = Fonction.objects.filter(user_fonction=request.user).select_related('fonction', 'service').first()
    if not myUser:
        return render(request, 'back/index.html', {'error': "Profil non trouvé."})

    role_affichage = myUser.fonction.type_fonction
    fonction_slug = str(role_affichage).strip().lower().replace('é', 'e')
    mon_service = myUser.service

    total_entrees = 0
    if "admin" in fonction_slug or "reception" in fonction_slug:
        total_entrees = Transaction.objects.aggregate(Sum('montant'))['montant__sum'] or 0

    context = {
        'userCount': User.objects.count(),
        'patientCount': Patient.objects.count(),
        'role_affichage': role_affichage,
        'fonction': fonction_slug,
        'mon_service': mon_service,
        'total_entrees': total_entrees,
    }

    if "admin" in fonction_slug:
        utilisateurs_list = Fonction.objects.all().select_related('user_fonction', 'fonction', 'service').order_by('user_fonction__username')
        paginator_u = Paginator(utilisateurs_list, 10)
        context['tous_les_utilisateurs'] = paginator_u.get_page(request.GET.get('page_u'))

    elif "reception" in fonction_slug:
        patients_list = Patient.objects.all().order_by('-id')
        paginator_p = Paginator(patients_list, 10)
        context['liste_patients'] = paginator_p.get_page(request.GET.get('page_p'))

    elif "infirmie" in fonction_slug:
        if mon_service:
            factures = Facture.objects.filter(patient__service_patient=mon_service, consultation__isnull=True).select_related('patient')
            context['file_attente'] = [f for f in factures if f.est_soldee]
            context['historique_service'] = Consultation.objects.filter(patient__service_patient=mon_service).select_related('patient', 'infirmier_triage').order_by('-date_creation')[:15]

    elif "medecin" in fonction_slug:
        if mon_service:
            context['file_attente'] = Consultation.objects.filter(statut='DOCTEUR', patient__service_patient=mon_service).select_related('patient').order_by('-date_creation')

    # --- AJOUT SECTION PHARMACIE ---
    elif "pharmacien" in fonction_slug:
        tous_produits = Produit.objects.all().select_related('famille')
        context['inventaire'] = tous_produits
        
        # Alertes de péremption (dans les 90 jours)
        limit_date = timezone.now().date() + timezone.timedelta(days=90)
        context['alertes_peremption'] = Lot.objects.filter(
            date_peremption__lte=limit_date, 
            quantite_actuelle__gt=0
        ).order_by('date_peremption')
    # --- FIN AJOUT ---

    return render(request, 'back/index.html', context)
# =============================================================
# formulaire de type de fonction 
# =============================================================
@login_required()
def type_fonction_add(request):

    msg = None 
    if request.method == 'POST':
        form = TypeFonctionForm(request.POST) 
        if form.is_valid():
            form.save()
            form = TypeFonctionForm(request.POST)
            msg = "information enregistre"

    form = TypeFonctionForm()        


    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 
    

    return render(request , 'back/type_fonction_add.html',{'fonction':fonction, 'form': form, 'msg':msg})  
# =============================================================
# enregistrement des employes 
# =============================================================
@login_required()
def employeAdd(request):
    msg = None
    if request.method =='POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            user = form.save(commit= False) 
            user.set_password(form.cleaned_data['password']) 
            user.save()
            # auth(request,user)
            
            form = EmployeForm(request.POST)
            msg = "employe enregistre "
        

    form = EmployeForm()

    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 
    return render(request,'back/employeAdd.html',{'fonction':fonction, 'form':form, 'msg':msg}) 
# =============================================================
# liste des employes 
# =============================================================
@login_required()
def employeRead(request):

    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    lst = User.objects.all()

    return render(request ,'back/employeRead.html', {'fonction': fonction , 'lst':lst}) 

# ==============================================================
# mise en jour employe 
# ==============================================================
@login_required()
def employeUpdate(request,id):
    call = User.objects.get(id = id)
    if request.method == 'POST':
        form = EmployeUpdateForm(request.POST , instance=call)
        if form.is_valid():
            form.save()
            return redirect('employeRead')

    form = EmployeUpdateForm(instance = call)        

    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    return render(request, 'back/employeUpdate.html',{'fonction':fonction,'form':form}) 

# =================================================================
# attribution de fonction est service
# =================================================================
@login_required()
def employeProfil(request,user_id):
    empl = get_object_or_404(User, id=user_id)
    profil, created = Fonction.objects.get_or_create(user_fonction=empl)
    msg = None 

    if request.method == 'POST':
        form = ProfilAddForm(request.POST , instance= profil)

        if form.is_valid():
            em = form.save(commit=False)

            em.user_fonction = empl
            em.save()

            return redirect('profilRead') 


    form = ProfilAddForm(instance= profil)    

    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 
    return render(request , 'back/employeProfil.html',{'fonction': fonction, 'form':form,'empl': empl})

# =================================================================
# profil read 
# =================================================================
@login_required()
def profilRead(request):

    lst = Fonction.objects.all()

    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    return render(request , 'back/profilRead.html',{'fonction':fonction,'lst': lst}) 

# =================================================================
# patient enregistrement 
# =================================================================
@login_required()
def patientAdd(request):
    msg = None 
    if request.method == 'POST':
        form = PatientForm(request.POST) 
        if form.is_valid():
            # 1. On prépare l'enregistrement du patient sans l'envoyer en BDD tout de suite
            patient = form.save(commit=False)
            
            # 2. On lie l'utilisateur qui fait l'enregistrement (Sécurité)
            patient.userPatient = request.user
            patient.save() # Le patient est maintenant créé avec son ID

            try:
                # 3. On récupère la prestation 'Fiche' (dynamique)
                prestation_fiche = Prestation.objects.get(est_fiche_obligatoire=True, active=True)
                
                # 4. On crée la facture AUTOMATIQUE pour ce nouveau patient
                Facture.objects.create(
                    patient=patient,
                    prestation=prestation_fiche
                    # Le montant sera récupéré via le save() du modèle Facture
                )
                
                return redirect('patientRead') 

            except Prestation.DoesNotExist:
                # Si la fiche n'est pas configurée, on informe l'utilisateur
                msg = "Patient créé, mais attention : la 'Fiche obligatoire' n'est pas configurée dans les prestations."
            except Exception as e:
                msg = f"Erreur lors de la création de la facture : {str(e)}"
    
    # Si GET ou si erreur
    form = PatientForm()
    
    # Gestion de la fonction utilisateur pour le template
    myUser = Fonction.objects.filter(user_fonction=request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    return render(request, 'back/patientAdd.html', {
        'fonction': fonction, 
        'form': form, 
        'msg': msg
    })

# ======================================================================
#  patient read
# ======================================================================
@login_required()
def patientRead(request):
    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    lst = Patient.objects.all().order_by('-id')

    return render(request , 'back/patientRead.html',{'fonction':fonction, 'lst':lst})  


# ========================================================================
# Faire payer une prestation (Fiche ou autre)
# =======================================================================

from django.db import transaction

@login_required()
def encaisser_prestation(request, patient_id=None, facture_id=None):
    patient = get_object_or_404(Patient, id=patient_id) if patient_id else None
    facture = get_object_or_404(Facture, id=facture_id) if facture_id else None

    if request.method == 'POST':
        form = EncaissementGlobalForm(request.POST, facture=facture)
        if form.is_valid():
            try:
                with transaction.atomic():
                    montant = form.cleaned_data.get('montant_verse')
                    prestation = form.cleaned_data.get('prestation')

                    # Création de facture si c'est le début
                    if not facture:
                        facture = Facture.objects.create(
                            patient=patient,
                            prestation=prestation,
                            total_a_payer=prestation.prix_fixe
                        )
                    
                    # Création du paiement
                    paiement = form.save(commit=False)
                    paiement.facture = facture
                    paiement.recepteur = request.user
                    paiement.save()

                    # Enregistrement en caisse
                    Transaction.objects.create(
                        agent=request.user,
                        montant=montant,
                        source='CONSULTATION',
                        ref_objet=str(facture.id)
                    )

                messages.success(request, f"Encaissement de {montant} FC validé.")
                return redirect('patientRead')
            except Exception as e:
                messages.error(request, f"Erreur : {e}")
    else:
        # Pré-remplissage si on vient d'une facture existante
        initial = {'prestation': facture.prestation} if facture else {}
        form = EncaissementGlobalForm(initial=initial, facture=facture)

    # On passe TOUTES les prestations pour le script JavaScript de contrôle de prix
    toutes_prestations = Prestation.objects.filter(active=True)

    return render(request, 'back/encaissement.html', {
        'form': form,
        'patient': patient or facture.patient,
        'facture': facture,
        'prestations': toutes_prestations
    })




# ============================================
# Voir l'historique d'un patient
# ============================================
def liste_factures_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    factures = Facture.objects.filter(patient=patient).order_by('-date_emission')

    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    return render(request, 'back/patientHistorique.html', {'patient': patient, 'factures': factures ,'fonction':fonction})

# =================================================
# imprime 
# =================================================
def imprimer_recu(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    # Pour le QR code, on récupère le paiement le plus récent
    dernier_paiement = facture.paiements.last()
    
    # --- GÉNÉRATION DU CODE QR ---
    # 1. On crée le contenu du QR Code : un lien de vérification unique
    # Exemple: http://votre-hopital.com/verifier-paiement/123/
    # Pour le test en local, on utilise l'ID de la facture comme preuve
    # Dans la réalité, on mettrait un hash de sécurité
    contenu_qr = f"Verif. Paiement GHOSPITAL\nFacture ID: {facture.id}\nPatient: {facture.patient.noms}\nMontant: {facture.total_a_payer} CDF\nStatut: {'Solde' if facture.est_soldee else 'Incomplet'}"
    
    # 2. Configuration du générateur QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(contenu_qr)
    qr.make(fit=True)

    # 3. Création de l'image en format SVG (plus propre pour l'impression)
    factory = qrcode.image.svg.SvgImage
    img = qr.make_image(image_factory=factory)
    
    # 4. Conversion de l'image SVG en texte pour l'inclure dans le HTML
    stream = BytesIO()
    img.save(stream)
    qr_svg_text = stream.getvalue().decode('utf-8')
    
    # --- FIN GÉNÉRATION ---

    context = {
        'facture': facture,
        'paiement': dernier_paiement,
        'hopital_nom': "G-HOSPITAL KINSHASA",
        'qr_code_svg': qr_svg_text, # On envoie le SVG directement au template
    }
    return render(request, 'back/recu_format_ticket.html', context)


# ================================================================================
# imprime recu par details
# ================================================================================
def imprimer_recu_tranche(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    facture = paiement.facture
    # Ici, chargez votre template de petit ticket (format 80mm généralement)
    return render(request, 'back/print/recu_tranche.html', {
        'paiement': paiement,
        'facture': facture,
        'patient': facture.patient
    })

# ==============================================================================
# imprimer gobal 
# ==============================================================================
def imprimer_recu(request, facture_id):
    # On récupère la facture et tous ses paiements d'un coup
    facture = get_object_or_404(Facture, id=facture_id)
    return render(request, 'back/print/facture_globale.html', {
        'facture': facture,
        'patient': facture.patient,
    })

# =================================================================================
# La Vue pour l'Infirmerie (Filtrage par Service)
# =================================================================================
@login_required
def tableau_bord_infirmier(request):
    # On suppose que l'utilisateur (infirmier) est lié à un service dans son profil
    service_infirmier = request.user.profil.service 
    
    # On ne récupère que les patients "En attente Infirmerie" de CE service
    patients_en_attente = Consultation.objects.filter(
        service=service_infirmier, 
        statut='TRIAGE'
    )
    
    return render(request, 'back/infirmerie/dashboard.html', {
        'patients': patients_en_attente
    })


# ==========================================================================
# signe vitaux
# ==========================================================================
@login_required()
def prelever_signes(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    if request.method == 'POST':
        # 1. Enregistrement des constantes
        consultation.temperature = request.POST.get('temperature')
        consultation.tension = request.POST.get('tension')
        consultation.poids = request.POST.get('poids')
        consultation.pouls = request.POST.get('pouls')
        
        # 2. Traçabilité : Qui et Quand ?
        consultation.infirmier_triage = request.user  # L'utilisateur connecté
        consultation.date_triage = timezone.now()
        
        # 3. Changement de Statut : Le patient passe vers le Médecin
        consultation.statut = 'DOCTEUR'
        
        consultation.save()
        
        messages.success(request, f"Prélèvement terminé pour {consultation.patient.noms}")
        return redirect('panel')
    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    return render(request, 'back/prelever_signes.html', {'consultation': consultation , 'fonction':fonction})

# ========================================================================================================
# medecin consultation 
# ========================================================================================================
@login_required()
def faire_consultation(request, consultation_id):
    # 1. Récupération de la consultation
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    if request.method == 'POST':
        # 2. Récupération des données du formulaire
        diagnostic_post = request.POST.get('diagnostic')
        ordonnance_post = request.POST.get('ordonnance')
        examens_ids = request.POST.getlist('examens')
        
        # Récupération de l'urgence
        est_urgent_post = request.POST.get('est_urgent') == 'on'
        message_urgence_post = request.POST.get('message_urgence')

        # 3. Enregistrement sécurisé avec une transaction
        with transaction.atomic():
            # Mise à jour des informations de base
            consultation.diagnostic = diagnostic_post
            consultation.ordonnance = ordonnance_post
            consultation.medecin = request.user  # Liaison au médecin connecté
            
            # Gestion de l'urgence
            consultation.est_urgent = est_urgent_post
            consultation.message_urgence = message_urgence_post if est_urgent_post else ""

            # 4. Gestion du flux (Statut)
            if examens_ids:
                # S'il y a des examens, le patient doit passer par la caisse/labo
                consultation.statut = 'ATTENTE_PAIEMENT'
                # On lie les examens (ManyToMany)
                consultation.examens_demandes.set(examens_ids)
                # Calcul du prix total basé sur les prestations choisies
                consultation.total_a_payer_examens = consultation.calculer_total_examens()
            else:
                # Sans examens, la consultation peut être clôturée ou envoyée en pharmacie
                consultation.statut = 'TERMINE'
                consultation.total_a_payer_examens = 0
                consultation.examens_demandes.clear()

            # Sauvegarde finale
            consultation.save()
            
        return redirect('panel')

    # 5. Préparation du mode GET (Affichage du formulaire)
    # On récupère toutes les prestations actives pour la liste de sélection
    tous_les_examens = Prestation.objects.filter(active=True).order_by('libelle')
    
    context = {
        'c': consultation,
        'tous_les_examens': tous_les_examens
    }
    
    return render(request, 'back/consultation_medecin.html', context)

# ====================================================================
# 1. REGISTRE DU JOUR (Tableau de bord de pointage)
# ====================================================================
@login_required()
def tableau_presence_reception(request):
    # --- 1. GESTION DE L'HEURE (18h au lieu de 10h) ---
    # On prend l'heure du PC pour ignorer les bugs de fuseau horaire
    maintenant = datetime.now()
    aujourdhui = maintenant.date()
    
    # --- 2. GESTION DU MENU (Variable 'fonction') ---
    # On récupère le profil de l'utilisateur connecté
    # IMPORTANT: Ton sidebar utilise la variable 'fonction'
    user_profil = Fonction.objects.filter(user_fonction=request.user).first()

    # --- 3. DONNÉES DU TABLEAU ---
    personnel_complet = Fonction.objects.select_related('user_fonction', 'service', 'fonction').all()
    presences_du_jour = Presence.objects.filter(date=aujourdhui)
    presence_dict = {p.employe_id: p for p in presences_du_jour}

    personnel_data = []
    for p in personnel_complet:
        pres = presence_dict.get(p.user_fonction.id)
        personnel_data.append({
            'emp': p.user_fonction,
            'poste': p.fonction.type_fonction if p.fonction else "Personnel",
            'service': p.service.nom if p.service else "Général",
            'presence': pres,
        })

    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    # --- 4. LE CONTEXTE (La clé du problème) ---
    context = {
        'personnel_data': personnel_data,
        'aujourdhui': aujourdhui,
        'fonction': fonction,  # C'est cette ligne qui fait apparaître le menu !
        'mon_profil': user_profil, # On met les deux au cas où
    }
    
    return render(request, 'back/gestion_presence.html', context)
# ======================================================================
#  pointer 
# ======================================================================
@login_required
def pointer_employe(request, user_id):
    # ON IGNORE DJANGO TIMEZONE ICI
    # On prend l'heure exacte de ton Windows/Serveur
    maintenant = datetime.now() 
    heure_actuelle = maintenant.time() 
    date_actuelle = maintenant.date()

    employe = get_object_or_404(User, id=user_id)
    
    presence, created = Presence.objects.get_or_create(
        employe=employe, 
        date=date_actuelle,
        defaults={'heure_arrivee': heure_actuelle, 'enregistre_par': request.user}
    )
    
    if not created:
        if not presence.heure_depart:
            presence.heure_depart = heure_actuelle
            presence.save()
            messages.success(request, f"Départ enregistré à {heure_actuelle.strftime('%H:%M')}")
        else:
            messages.warning(request, "Déjà pointé pour aujourd'hui.")
    else:
        messages.success(request, f"Arrivée enregistrée à {heure_actuelle.strftime('%H:%M')}")
        
    return redirect('presence_reception')

# =====================================================================
# 3. HISTORIQUE DE PRESENCE (Archives)
# =====================================================================
@login_required
def historique_presences(request):
    # 1. RÉCUPÉRATION DE LA DATE DEPUIS LE FORMULAIRE (Le bouton Filtrer)
    date_str = request.GET.get('date_selectionnee')
    if date_str:
        try:
            date_recherche = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date_recherche = datetime.now().date()
    else:
        date_recherche = datetime.now().date()

    # 2. RÉCUPÉRATION DES PRÉSENCES FILTRÉES PAR DATE
    # On utilise select_related pour ne pas ralentir le serveur
    presences_list = Presence.objects.filter(date=date_recherche).select_related('employe').order_by('-heure_arrivee')

    # 3. RÉCUPÉRATION DES FONCTIONS POUR LE TABLEAU
    toutes_les_fonctions = Fonction.objects.select_related('fonction', 'service').all()
    fonctions_dict = {f.user_fonction_id: f for f in toutes_les_fonctions}

    historique_complet = []
    for p in presences_list:
        f_info = fonctions_dict.get(p.employe.id)
        
        historique_complet.append({
            'date': p.date,
            'nom': p.employe.get_full_name() or p.employe.username,
            'poste': f_info.fonction.type_fonction if f_info and f_info.fonction else "Personnel",
            'service': f_info.service.nom if f_info and f_info.service else "Général",
            'arrivee': p.heure_arrivee,
            'depart': p.heure_depart,
        })

    # 4. PRÉPARATION DU MENU (SIDEBAR)
    # On envoie l'objet COMPLET pour que le menu puisse lire toutes les infos
    myUser_profil = Fonction.objects.select_related('fonction', 'service').filter(user_fonction=request.user).first()

    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    context = {
        'historique': historique_complet,
        'date_recherche': date_recherche, # Indispensable pour garder la date dans l'input
        'fonction': fonction,        # Ton menu sidebar va enfin s'ouvrir
        'aujourdhui': datetime.now().date(),
    }
    return render(request, 'back/historique_presence.html', context)

# ============================================================================
# stati presence de chaque employe 
# ============================================================================
@login_required
def statistiques_presence(request):
    # 1. Menu Sidebar (toujours envoyer 'fonction')
    user_profil = Fonction.objects.filter(user_fonction=request.user).first()

    # 2. Récupérer tous les employés et leurs fonctions
    employes_fonctions = Fonction.objects.select_related('user_fonction', 'service', 'fonction').all()
    
    # 3. Calculer les stats par employé
    stats_data = []
    # On définit une période (ex: ce mois-ci ou depuis toujours)
    total_jours_enregistres = Presence.objects.values('date').distinct().count()

    for emp_f in employes_fonctions:
        # Compter combien de fois cet employé apparaît dans la table Presence
        jours_presents = Presence.objects.filter(employe=emp_f.user_fonction).count()
        
        # Calcul du pourcentage (éviter division par zéro)
        taux = (jours_presents / total_jours_enregistres * 100) if total_jours_enregistres > 0 else 0

        stats_data.append({
            'nom': emp_f.user_fonction.get_full_name() or emp_f.user_fonction.username,
            'poste': emp_f.fonction.type_fonction if emp_f.fonction else "Personnel",
            'service': emp_f.service.nom if emp_f.service else "Général",
            'total_presences': jours_presents,
            'taux': round(taux, 1),
            # Statut visuel
            'performance': 'success' if taux >= 80 else 'warning' if taux >= 50 else 'danger'
        })
    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    context = {
        'stats': stats_data,
        'total_jours': total_jours_enregistres,
        'fonction': fonction, # Pour le menu
    }
    return render(request, 'back/statistiques_presence.html', context)

# ===================================================================================
# generer presence des employes en pdf 
# ===================================================================================
@login_required()
def generer_pdf_presence(request):
    # 1. Récupération des données (identique à ton historique)
    presences_list = Presence.objects.select_related('employe').all().order_by('-date', '-heure_arrivee')
    fonctions_dict = {f.user_fonction_id: f for f in Fonction.objects.select_related('fonction', 'service').all()}

    historique_complet = []
    for p in presences_list:
        f_info = fonctions_dict.get(p.employe.id)
        historique_complet.append({
            'date': p.date,
            'nom': p.employe.get_full_name() or p.employe.username,
            'poste': f_info.fonction.type_fonction if f_info and f_info.fonction else "Personnel",
            'service': f_info.service.nom if f_info and f_info.service else "Général",
            'arrivee': p.heure_arrivee,
            'depart': p.heure_depart,
        })

    # 2. Préparation du PDF
    template_path = 'back/pdf_presence.html'
    context = {
        'historique': historique_complet,
        'date_edition': datetime.now(),
    }
    
    response = HttpResponse(content_type='application/pdf')
    # 'attachment' pour télécharger, 'inline' pour ouvrir dans le navigateur
    response['Content-Disposition'] = 'attachment; filename="rapport_presences.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    # Création du PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
       return HttpResponse('Erreur lors de la génération du PDF', status=500)
    return response

# =======================================================================
# ajout du materiel 
# =======================================================================
def ajouter_materiel(request):
    # Pour le sidebar (on garde la cohérence)
    myUser = Fonction.objects.filter(user_fonction=request.user).first()
    type_role = myUser.fonction.type_fonction.lower() if myUser and myUser.fonction else ""

    if request.method == "POST":
        # Récupération des données du formulaire
        designation = request.POST.get('designation')
        categorie_id = request.POST.get('categorie')
        quantite = request.POST.get('quantite')
        seuil = request.POST.get('seuil')
        unite = request.POST.get('unite')

        # Création de l'objet dans la base de données
        categorie_obj = Categorie.objects.get(id=categorie_id)
        
        Materiel.objects.create(
            designation=designation,
            categorie=categorie_obj,
            quantite_stock=quantite,
            seuil_alerte=seuil,
            unite_mesure=unite
        )
        
        messages.success(request, f"Le matériel '{designation}' a été enregistré avec succès.")
        return redirect('liste_materiel') # On redirigera vers la liste après

    # On récupère les catégories pour le menu déroulant du formulaire
    categories = Categorie.objects.all()
    
    context = {
        'categories': categories,
        'fonction': type_role,
    }
    return render(request, 'back/ajouter_materiel.html', context)

# =================================================================
# liste de materiel 
# =================================================================
@login_required
def liste_materiel(request):
    # Récupération du profil pour le sidebar
    myUser = Fonction.objects.filter(user_fonction=request.user).first()
    type_role = myUser.fonction.type_fonction.lower() if myUser and myUser.fonction else ""

    # Récupération de tous les articles en stock
    tous_les_materiels = Materiel.objects.select_related('categorie').all()

    context = {
        'materiels': tous_les_materiels,
        'fonction': type_role,
    }
    return render(request, 'back/liste_materiel.html', context)

# ================================================================
# ajout de categorie 
# ================================================================
@login_required()
def gestion_categories(request):
    # Pour le sidebar
    myUser = Fonction.objects.filter(user_fonction=request.user).first()
    if not myUser or myUser.fonction.type_fonction.lower() != 'admin':
        return redirect('panel') # Sécurité : seul l'admin passe

    if request.method == "POST":
        nom_categorie = request.POST.get('nom')
        if nom_categorie:
            # Création de la catégorie
            Categorie.objects.create(nom=nom_categorie)
            messages.success(request, f"La catégorie '{nom_categorie}' a été ajoutée.")
            return redirect('gestion_categories')

    # On récupère toutes les catégories pour les afficher dans un tableau
    categories = Categorie.objects.all().order_by('nom')
    
    context = {
        'categories': categories,
        'fonction': 'admin',
    }
    return render(request, 'back/gestion_categories.html', context)

# ============================================================================================
# prestation add 
# ============================================================================================
@login_required()
def prestation_add(request):
    msg = None
    
    # 1. On récupère la fonction de l'utilisateur pour le Sidebar
    # C'est ce qui permet de garder le menu 'Admin' affiché
    myUser = Fonction.objects.filter(user_fonction=request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    if request.method == 'POST':
        form = PrestationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('prestation_list')
        else:
            msg = "Erreur lors de l'enregistrement. Vérifiez les données."
    else:
        form = PrestationForm()
    
    # 2. On ajoute 'fonction' dans le dictionnaire de retour
    return render(request, 'back/prestation_add.html', {
        'form': form, 
        'msg': msg, 
        'fonction': fonction
    })
# ==========================================================================================
# 
# ==========================================================================================
@login_required()
def prestation_list(request):
    # On récupère toutes les prestations enregistrées
    prestations = Prestation.objects.all().order_by('type_prestation', 'libelle')
    
    # On récupère la fonction de l'utilisateur pour le menu (comme dans tes autres vues)
    myUser = Fonction.objects.filter(user_fonction=request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    return render(request, 'back/prestation_list.html', {
        'prestations': prestations,
        'fonction': fonction
    })
# =======================================================================================
# modifier prestation
# =======================================================================================

@login_required()
def prestation_edit(request, pk):
    # Fonction pour modifier un prix existant
    
    prestation = get_object_or_404(Prestation, pk=pk)
    if request.method == 'POST':
        form = PrestationForm(request.POST, instance=prestation)
        if form.is_valid():
            form.save()
            return redirect('prestation_list')
    else:
        form = PrestationForm(instance=prestation)

    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None

    return render(request, 'back/prestation_add.html', {'form': form, 'edit_mode': True , 'fonction':fonction})

# =============================================================================================
#
# ============================================================================================
@login_required()
def encaisser_examen(request, consultation_id):
    # On récupère la consultation en attente de paiement
    c = get_object_or_404(Consultation, id=consultation_id)
    
    if request.method == 'POST':
        # Logique d'encaissement
        c.paiement_examens_effectue = True
        c.statut = 'LABO' # Le patient peut maintenant aller au labo
        c.date_paiement = timezone.now() # Si tu as ce champ
        c.save()
        
        messages.success(request, f"Paiement de {c.total_a_payer_examens} CDF confirmé pour {c.patient.noms}")
        return redirect('panel')

    context = {
        'c': c,
    }
    return render(request, 'back/caisse_paiement.html', context)

# ==============================================================================================
# ajoute tranche 
# ==============================================================================================
@login_required()
def ajouter_tranche(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    
    if request.method == 'POST':
        montant = request.POST.get('montant_verse')
        if montant:
            # On enregistre la nouvelle tranche
            Paiement.objects.create(
                facture=facture,
                montant_verse=montant,
                recepteur=request.user # La personne connectée qui encaisse
            )
            # Pas besoin de modifier le statut ici, ton modèle Facture 
            # le fera tout seul dans son save() si le reste tombe à 0 !
            return redirect('panel')

    return render(request, 'back/ajouter_tranche.html', {'facture': facture})




# =============================================================================================
# gestion de document 
# =============================================================================================
@login_required()
def gestion_documents(request):
    # Récupérer le rôle
    user_profil = Fonction.objects.filter(user_fonction=request.user).first()
    fonction = user_profil.fonction.type_fonction if user_profil else ""

    # Filtrage par recherche
    query = request.GET.get('search')
    if query:
        documents = DocumentHospitalier.objects.filter(titre__icontains=query).order_by('-date_creation')
    else:
        documents = DocumentHospitalier.objects.all().order_by('-date_creation')

    if request.method == "POST":
        # Logique d'upload pour le Réceptionniste ou l'Admin
        titre = request.POST.get('titre')
        fichier = request.FILES.get('fichier')
        type_doc = request.POST.get('type_doc')
        
        DocumentHospitalier.objects.create(
            titre=titre,
            fichier=fichier,
            type_document=type_doc,
            ajoute_par=request.user
        )
        return redirect('gestion_documents')

    context = {
        'documents': documents,
        'fonction': fonction,
    }
    return render(request, 'back/documents.html', context)

# =========================================================================================================
#supprimer le document 
# =========================================================================================================
@login_required()
def supprimer_document(request, doc_id):
    # Sécurité : Vérifier si l'utilisateur est admin
    user_profil = Fonction.objects.filter(user_fonction=request.user).first()
    if not user_profil or user_profil.fonction.type_fonction != 'admin':
        messages.error(request, "Accès refusé. Seul l'administrateur peut supprimer des documents.")
        return redirect('gestion_documents')

    # Récupérer le document
    doc = get_object_or_404(DocumentHospitalier, id=doc_id)
    
    # Supprimer le fichier réel sur le disque dur (MacBook)
    if doc.fichier:
        if os.path.isfile(doc.fichier.path):
            os.remove(doc.fichier.path)
    
    # Supprimer l'entrée en base de données
    doc.delete()
    
    messages.success(request, "Le document a été définitivement supprimé.")
    return redirect('gestion_documents')


# ===================================================================================
# consutation 
@login_required()
def creer_consultation(request, facture_id):
    # On récupère la facture payée
    facture = get_object_or_404(Facture, id=facture_id)
    
    if request.method == 'POST':
        # On récupère les données du formulaire (Signes vitaux)
        poids = request.POST.get('poids')
        temperature = request.POST.get('temperature')
        tension = request.POST.get('tension')
        
        # On crée la consultation avec le statut 'DOCTEUR' 
        # pour qu'elle apparaisse chez le médecin
        nouvelle_consultation = Consultation.objects.create(
            patient=facture.patient,
            service=facture.prestation.service, # On garde le même service
            poids=poids,
            temperature=temperature,
            tension=tension,
            statut='DOCTEUR', # Envoi direct au médecin
            infirmier_triage=request.user # L'infirmier connecté
        )
        
        # On lie la facture à cette nouvelle consultation
        facture.consultation = nouvelle_consultation
        facture.save()
        
        messages.success(request, f"Constantes enregistrées pour {facture.patient.noms}. Patient envoyé au médecin.")
        return redirect('panel')

    return render(request, 'back/creer_consultation.html', {'facture': facture})
    # ===================================================================================================
    #
    # ====================================================================================================
@login_required()
def prelever_signes(request, consultation_id):
    # Récupération de la consultation créée à l'accueil
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    if request.method == 'POST':
        # 1. Récupération des données du formulaire HTML
        consultation.temperature = request.POST.get('temperature')
        consultation.tension = request.POST.get('tension')
        consultation.poids = request.POST.get('poids')
        consultation.pouls = request.POST.get('pouls')
        # Gestion de l'urgence (checkbox)
        consultation.est_urgent = request.POST.get('est_urgent') == 'True'
        
        # 2. Traçabilité
        consultation.infirmier_triage = request.user
        consultation.date_triage = timezone.now()
        
        # 3. Changement de Statut pour envoyer au médecin
        consultation.statut = 'DOCTEUR'
        consultation.save()
        
        messages.success(request, f"Constantes de {consultation.patient.noms} envoyées au médecin.")
        return redirect('panel')

    # Gestion de la sidebar et du rôle
    myUser = Fonction.objects.filter(user_fonction=request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    return render(request, 'back/prelever_signes.html', {
        'consultation': consultation, 
        'fonction': fonction
    })

# ======================================================================================================
# ajout des stocks 
# ======================================================================================================
@login_required()
def ajouter_stock(request):
    if request.method == "POST":
        try:
            # Récupération des données du formulaire
            produit_id = request.POST.get('produit_id')
            numero_lot = request.POST.get('numero_lot')
            qte_boites = int(request.POST.get('quantite_boites', 0))
            prix_achat_boite = Decimal(request.POST.get('prix_achat_boite', 0))
            date_peremption = request.POST.get('date_peremption')

            # Validation de base
            if qte_boites <= 0 or prix_achat_boite <= 0:
                messages.error(request, "La quantité et le prix doivent être supérieurs à zéro.")
                return redirect('panel')

            produit = get_object_or_404(Produit, id=produit_id)

            # Calculs
            # Conversion : ex 10 boites de 30 comprimés = 300 unités de détail
            total_unites = qte_boites * produit.coefficient_conversion
            # Coût total de l'achat pour la caisse
            cout_total = qte_boites * prix_achat_boite

            # Utilisation d'une transaction atomique pour garantir que 
            # le stock et la finance sont mis à jour ensemble
            with transaction.atomic():
                # 1. Création du Lot
                nouveau_lot = Lot.objects.create(
                    produit=produit,
                    numero_lot=numero_lot,
                    quantite_initiale=total_unites,
                    quantite_actuelle=total_unites,
                    prix_achat_total_lot=cout_total,
                    date_peremption=date_peremption
                )

                # 2. Enregistrement du mouvement de stock (Traçabilité)
                MouvementStock.objects.create(
                    produit=produit,
                    lot=nouveau_lot,
                    type_mouvement='ENTREE',
                    quantite=total_unites,
                    motif=f"Achat de {qte_boites} boîtes",
                    agent=request.user
                )

                # 3. Enregistrement de la dépense en finance (SORTIE de caisse)
                Transaction.objects.create(
                    montant=cout_total,
                    description=f"Achat Stock : {produit.designation} (Lot {numero_lot})",
                    type_transaction='SORTIE',
                    agent=request.user
                )

            messages.success(request, f"Entrée réussie : {total_unites} unités de {produit.designation} ajoutées.")
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout : {str(e)}")
            
    return redirect('panel')