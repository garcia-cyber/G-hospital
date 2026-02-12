from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# creation de la table programme pour bloque le programme 
# =======================================================
# =======================================================
class Programme(models.Model):
    statutProgramme = models.CharField(default='ouii', max_length=10) 
    dateProgramme = models.DateField(auto_now_add=True) 

    def __str__(self):
        return self.statutProgramme 
    
# creation de la table type_fonction pour parametre les fonctions 
# ===============================================================
# ===============================================================
class TypeFonction(models.Model):
    type_fonction = models.CharField(max_length=30) 

    def __str__(self):
        return self.type_fonction


#
# ================= creation de la table poste 
# =================
# =================

class Fonction(models.Model):
    fonction = models.ForeignKey(TypeFonction , on_delete= models.CASCADE) 
    user_fonction = models.ForeignKey(User, on_delete= models.CASCADE) 
    TYPE = [
        ('Actif','actif') ,
        ('Bloque','bloque')
    ]
    statut_fonction = models.CharField(max_length=10 , choices=TYPE) 

    # def __str__(self):
    #     return self.user_fonction

