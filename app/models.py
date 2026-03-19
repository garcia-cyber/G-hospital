from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

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

# creation de la table service pour parametre les fonctions 
# ===============================================================
# ===============================================================
class Service(models.Model):
    service = models.CharField(max_length = 50) 

    def __str__(self):
        return self.service 
    
    
# ===========================================================
# commune 
# ===========================================================
class Commune(models.Model):
    nomCommune = models.CharField(max_length= 80)

    def __str__(self):
        return self.nomCommune
    


# ==============================================================
# creation de la table poste 
# ==============================================================


class Fonction(models.Model):
    fonction = models.ForeignKey(TypeFonction , on_delete= models.SET_NULL , null = True) 
    user_fonction = models.ForeignKey(User, on_delete= models.SET_NULL , null = True) 
    TYPE = [
        ('Actif','actif') ,
        ('Bloque','bloque')
    ]
    statut_fonction = models.CharField(max_length=10 , choices=TYPE , default= 'actif') 
    service = models.ForeignKey(Service , on_delete= models.SET_NULL , null = True)
    adresse = models.CharField(max_length= 80 , null= True) 
    TYPEETAT = [
        ('celibateur','Celibateur') ,
        ('marie','Marie') ,
        ('divorce','Divorce') 
    ]
    etatCivil = models.CharField(max_length=30 , null = True, choices= TYPEETAT) 
    phone = models.IntegerField(null = True) 
    TYPECOMMUNE = [
        ('limete','Limete') ,
        ('masina','Masina') , 
        ('matete', 'Matete') , 
        ('lemba', 'Lemba') , 
        ("n'djili", "N'djili" ),
        ('ngaliema', 'Ngaliema') , 
        ('gombe','Gombe')
    ]
    commune = models.CharField(max_length=50 , null = True, choices=TYPECOMMUNE)
    

    def __str__(self):
        return self.statut_fonction

# ====================================================================
# creation de la table patient 
# ====================================================================
class Patient(models.Model):
    noms = models.CharField(max_length=80)
    TYPE = [
        ('Masculin', 'masculin') , 
        ('Feminin','feminin')
    ]
    sexe = models.CharField(max_length=15 , choices= TYPE)
    age  = models.IntegerField()
    adresse = models.CharField(max_length=100)
    poids = models.IntegerField()
    dateEn = models.DateTimeField(auto_now_add= True) 
    phone_responsable = models.IntegerField(null=True) 
    userPatient = models.ForeignKey(User, on_delete= models.CASCADE , null= True)
    TYPECOMMUNE = [
        ('limete','Limete') ,
        ('masina','Masina') , 
        ('matete', 'Matete') , 
        ('lemba', 'Lemba') , 
        ("n'djili", "N'djili" ),
        ('ngaliema', 'Ngaliema') , 
        ('gombe','Gombe')
    ]
    commune = models.CharField(max_length=50 , null = True, choices=TYPECOMMUNE)
    service_patient = models.ForeignKey(Service , on_delete= models.SET_NULL , null = True)


    def __str__(self):
        return self.noms 

    class Meta :
        ordering = ['-id']

# =========================================================================
# creation de la table commune 
# =========================================================================
class Commune(models.Model):
    nomCommune = models.CharField(max_length=30 )

    def __str__(self):
        return self.nomCommune
    
# ===========================================================================
# creation de la table stagiaire 
# ===========================================================================
class Stagiare(models.Model):
    nomStagiaires = models.CharField(max_length=80)
    TYPESEXE = [
        ('Masculin','masculin') ,
        ("Feminin", 'feminin')
    ]
    sexe = models.CharField(choices=TYPESEXE, max_length=20) 
    phone = models.IntegerField()
    commune = models.ForeignKey(Commune , on_delete=models.CASCADE) 
    adresse = models.CharField(max_length=50) 
    TYPESTAGE = [
        ('Professionnel','professionnel') , 
        ('Academique','academique')
    ]
    type_stage = models.CharField(max_length=30 ,choices=TYPESTAGE) 
    dateDebut = models.DateField()
    dateFin   = models.DateField()
    userStagiaire = models.ForeignKey(User , on_delete= models.CASCADE)
    stagiairename = models.CharField(max_length=40)
    password = models.CharField(max_length=150)
    dateRegistereStagiaire = models.DateTimeField(auto_now_add=True , null = True)

    def __str__(self):
        return self.nomStagiaires

# ==============================================================================
# prestations 
# ==============================================================================
class Prestation(models.Model):
    libelle = models.CharField(max_length=100) # Ex: "Fiche", "Opération"
    prix_fixe = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.libelle 

# ===============================================================================
# facture 
# =============================================================================

from django.db.models import Sum

from django.db import models
from django.db.models import Sum


# ============================================
# facture 
# ============================================

class Facture(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prestation = models.ForeignKey(Prestation, on_delete=models.CASCADE)
    total_a_payer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_emission = models.DateTimeField(auto_now_add=True)

    @property
    def nom_service(self):
        """Récupère dynamiquement le nom du service lié à la prestation"""
        if self.prestation and hasattr(self.prestation, 'service'):
            # On suppose que votre modèle Prestation a une ForeignKey vers Service
            return self.prestation.service.nom
        return "Service Non Défini"

    @property
    def total_verse(self):
        """Calcule la somme de tous les paiements effectués"""
        resultat = self.paiements.aggregate(Sum('montant_verse'))['montant_verse__sum']
        return resultat or 0

    @property
    def reste_a_payer(self):
        """Calcule le reste à percevoir"""
        return self.total_a_payer - self.total_verse

    @property
    def est_soldee(self):
        """Vérifie si la facture est totalement payée"""
        return self.reste_a_payer <= 0

    def save(self, *args, **kwargs):
        """Sécurité : récupère le prix de la prestation si non précisé"""
        if not self.total_a_payer and self.prestation:
            self.total_a_payer = self.prestation.prix_fixe
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_emission']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def __str__(self):
        # On inclut le service dans le nom pour plus de clarté
        status = "SOLDEE" if self.est_soldee else f"RESTE: {self.reste_a_payer} CDF"
        return f"Facture {self.id} [{self.nom_service}] - {self.patient.noms} ({status})"


# ================================================================================
# paiement
# ================================================================================

from django.db import transaction

from django.db import models
from django.db.models import Q

class Paiement(models.Model):
    facture = models.ForeignKey('Facture', on_delete=models.CASCADE, related_name='paiements')
    montant_verse = models.DecimalField(max_digits=12, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    caissier = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # 1. Enregistrement normal
        super().save(*args, **kwargs)

        # 2. Si la facture est soldée, on gère l'envoi au service
        if self.facture.est_soldee:
            from .models import Consultation, Fonction, Notification # Import local pour éviter les boucles
            
            # Vérifier si c'est une fiche et si la consultation n'existe pas déjà
            exists = Consultation.objects.filter(facture=self.facture).exists()
            
            if not exists and "fiche" in self.facture.prestation.libelle.lower():
                # Création de la ligne de consultation (Direction Triage)
                consultation = Consultation.objects.create(
                    patient=self.facture.patient,
                    facture=self.facture,
                    service=self.facture.prestation.service,
                    statut='TRIAGE'
                )

                # --- LOGIQUE DE NOTIFICATION PAR SERVICE ---
                # On cherche tous les agents (infirmiers/médecins) ACTIFS de ce service précis
                service_concerne = self.facture.prestation.service
                personnels_du_service = Fonction.objects.filter(
                    service=service_concerne,
                    statut_fonction='Actif'
                )

                # On crée une notification pour chaque membre du service
                for p in personnels_du_service:
                    Notification.objects.create(
                        user=p.user_fonction, # L'utilisateur lié à la fonction
                        titre="Nouveau Patient",
                        message=f"Le patient {self.facture.patient.noms} a payé sa fiche. Il attend au triage.",
                        service_origine=service_concerne
                    )

    def __str__(self):
        return f"Paiement de {self.montant_verse} pour Facture #{self.facture.id}"
# ==================================================================================
# consultation 
# ==================================================================================
class Consultation(models.Model):
    STATUT_CHOICES = [
        ('TRIAGE', 'En attente Infirmerie'),
        ('DOCTEUR', 'En attente Médecin'),
        ('LABO', 'En attente Labo'),
        ('TERMINE', 'Terminé'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    facture = models.OneToOneField(Facture, on_delete=models.CASCADE) # Lié à la fiche payée
    service = models.ForeignKey(Service, on_delete=models.CASCADE) # Ex: Pédiatrie
    
    # Signes vitaux (remplis par l'infirmier)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    poids = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tension = models.CharField(max_length=20, null=True, blank=True)
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='TRIAGE')
    date_creation = models.DateTimeField(auto_now_add=True)




# ===============================================================================
# notification (Comment l'infirmier reçoit-il le message ?)
# ================================================================================
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # L'infirmier ou médecin
    titre = models.CharField(max_length=100)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)
    service_origine = models.ForeignKey('Service', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Alerte pour {self.user.username} - {self.titre}"