from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth import authenticate , login as auth , logout 
from django.contrib.auth.decorators import login_required 
from .forms import LoginForm , TypeFonctionForm ,EmployeForm , EmployeUpdateForm  , PatientForm
from .models import Fonction
from django.contrib.auth.models import User
from .models import * 
from .forms import  *
import qrcode
import qrcode.image.svg
from io import BytesIO
from django.contrib import messages # N'oubliez pas cet import tout en haut

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
    return redirect('login')

# ============================================================
# panel controle 
# =============================================================
@login_required()
def panel(request):

    userCount = User.objects.count()
    patientCount = Patient.objects.count()
    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    
    

    # fonction
    fonction = myUser.fonction.type_fonction if myUser else None 

    context = {
        'fonction':fonction ,
        'userCount':userCount ,
        'patientCount':patientCount ,  
        
        }

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
            patient =form.save()
            if request.user.is_authenticated:
                patient.userPatient = request.user
                patient.save()
                # msg ='information enregistre'
                # form = PatientForm(request.POST) 
                return redirect('patientRead') 
            else:
                msg = 'erreur du systeme'
                
                

    form = PatientForm()
    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    return render(request , 'back/patientAdd.html' , {'fonction':fonction, 'form':form , 'msg':msg})

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

def encaisser_prestation(request, patient_id=None, facture_id=None):
    facture = None
    patient = None

    # ON TESTE LE PATIENT EN PREMIER
    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)
    # ENSUITE LA FACTURE
    elif facture_id:
        facture = get_object_or_404(Facture, id=facture_id)
        patient = facture.patient
    else:
        return redirect('patientRead') # Remplacez par votre nom de vue de liste

    # --- TRAITEMENT DU FORMULAIRE ---
    if request.method == 'POST':
        form = EncaissementForm(request.POST)
        if form.is_valid():
            montant = form.cleaned_data['montant_verse']
            
            # CAS 1 : NOUVELLE FACTURE
            if not facture:
                prestation = form.cleaned_data.get('prestation')
                if not prestation:
                    messages.error(request, "Veuillez choisir une prestation.")
                else:
                    # Création de la facture initiale
                    facture = Facture.objects.create(
                        patient=patient,
                        prestation=prestation,
                        total_a_payer=prestation.prix_fixe
                    )
                    Paiement.objects.create(facture=facture, montant_verse=montant)
                    messages.success(request, "Encaissement réussi.")
                    return redirect('liste_factures_patient', patient_id=patient.id)
            
            # CAS 2 : PAIEMENT D'UNE DETTE EXISTANTE
            else:
                if montant > facture.reste_a_payer:
                    messages.error(request, f"Le montant dépasse le reste dû ({facture.reste_a_payer} CDF).")
                else:
                    Paiement.objects.create(facture=facture, montant_verse=montant)
                    messages.success(request, "Versement enregistré.")
                    return redirect('liste_factures_patient', patient_id=patient.id)
    else:
        # Initialisation du formulaire
        initial_data = {}
        if facture:
            initial_data['prestation'] = facture.prestation
            initial_data['montant_verse'] = facture.reste_a_payer
        form = EncaissementForm(initial=initial_data)

    prestations = Prestation.objects.all()
    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 

    return render(request, 'back/encaissement.html', {
        'form': form,
        'patient': patient,
        'facture': facture,
        'prestations': prestations ,
        'fonction':fonction 
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