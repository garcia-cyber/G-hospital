from django.shortcuts import render , redirect 
from django.contrib.auth import authenticate , login as auth , logout 
from django.contrib.auth.decorators import login_required 
from .forms import LoginForm , TypeFonctionForm ,EmployeForm
from .models import Fonction
from django.contrib.auth.models import User

# Create your views here.


#==============================
#============================== login 
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

#
# ========================================= deconnexion ======================
#
def deco(request):
    logout(request)
    return redirect('login')
#
# ================================
# ================================ panel controle 
@login_required()
def panel(request):

    userCount = User.objects.count()
    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    
    

    # fonction
    fonction = myUser.fonction.type_fonction if myUser else None 

    context = {
        'fonction':fonction ,
        'userCount':userCount ,  
        
        }

    return render(request, 'back/index.html', context) 

#
# ==================== formulaire de type de fonction 
# ===================================================
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

#
# ==================== enregistrement des employes 
# ===================================================
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