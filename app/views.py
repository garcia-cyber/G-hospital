from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth import authenticate , login as auth , logout 
from django.contrib.auth.decorators import login_required 
from .forms import LoginForm , TypeFonctionForm ,EmployeForm , EmployeUpdateForm  , PatientForm
from .models import Fonction
from django.contrib.auth.models import User
from .models import * 
from .forms import  *

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
                msg ='information enregistre'
                form = PatientForm(request.POST) 
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

    lst = Patient.objects.all()

    return render(request , 'back/patientRead.html',{'fonction':fonction, 'lst':lst})  

