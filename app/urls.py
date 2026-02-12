from django.urls import path  
from .views import login , panel , deco
from .views import * 


urlpatterns = [
    path('login/', login , name='login') , 
    path('panel/', panel , name = 'panel') , 
    path('deco/', deco , name='deco'),
    path('typeFonctionAdd/', type_fonction_add , name='type_fonction_add') , 
    path('employeAdd', employeAdd , name = 'employeAdd') , 
]
