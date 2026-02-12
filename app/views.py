from django.shortcuts import render , redirect 
from django.contrib.auth import authenticate , login as auth , logout 
from django.contrib.auth.decorators import login_required 
from .forms import LoginForm , TypeFonctionForm 
from .models import Fonction

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

    
    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    
    

    # fonction
    fonction = myUser.fonction.type_fonction if myUser else None 


    return render(request, 'back/index.html', {'fonction':fonction }) 

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
            form = TypeFonctionForm()
            msg = "information enregistre"

    form = TypeFonctionForm()        


    myUser = Fonction.objects.filter(user_fonction = request.user).first()
    fonction = myUser.fonction.type_fonction if myUser else None 
    

    return render(request , 'back/type_fonction_add.html',{'fonction':fonction, 'form': form, 'msg':msg})  