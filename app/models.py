from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.conf import settings # Pour lier l'utilisateur connecté
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
# =======================================================
# 1. PARAMETRAGES DE BASE
# =======================================================

class Programme(models.Model):
    statutProgramme = models.CharField(default='ouii', max_length=10) 
    dateProgramme = models.DateField(auto_now_add=True) 

    def __str__(self):
        return self.statutProgramme 

class TypeFonction(models.Model):
    type_fonction = models.CharField(max_length=30) 

    def __str__(self):
        return self.type_fonction

class Service(models.Model):
    # Correction : On utilise 'nom' au lieu de 'service'
    nom = models.CharField(max_length=50) 

    def __str__(self):
        return self.nom 

class Commune(models.Model):
    nomCommune = models.CharField(max_length=80)

    def __str__(self):
        return self.nomCommune

# ==============================================================
# 2. GESTION DU PERSONNEL (FONCTION) - PLACÉ ICI POUR ÊTRE RECONNU
# ==============================================================

class Fonction(models.Model):
    fonction = models.ForeignKey(TypeFonction, on_delete=models.SET_NULL, null=True) 
    user_fonction = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='profil_fonction') 
    
    TYPE_STATUT = [('Actif','actif'), ('Bloque','bloque')]
    statut_fonction = models.CharField(max_length=10, choices=TYPE_STATUT, default='actif') 
    
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    adresse = models.CharField(max_length=80, null=True, blank=True) 
    
    TYPE_ETAT = [('celibateur','Célibataire'), ('marie','Marié'), ('divorce','Divorcé')]
    etatCivil = models.CharField(max_length=30, null=True, choices=TYPE_ETAT) 
    
    phone = models.CharField(max_length=20, null=True, blank=True) 

    def __str__(self):
        return f"{self.user_fonction.username if self.user_fonction else 'Sans utilisateur'}"

# ====================================================================
# 3. GESTION DES PATIENTS
# ====================================================================

# ==============================================================================
# 3. PATIENTS
# ==============================================================================

class Patient(models.Model):
    noms = models.CharField(max_length=80)
    TYPE_SEXE = [('Masculin', 'masculin'), ('Feminin','feminin')]
    sexe = models.CharField(max_length=15, choices=TYPE_SEXE)
    age = models.IntegerField()
    adresse = models.CharField(max_length=100)
    poids = models.IntegerField()
    dateEn = models.DateTimeField(auto_now_add=True) 
    phone_responsable = models.CharField(max_length=20, null=True, blank=True) 
    userPatient = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    TYPECOMMUNE = [
        ('limete','Limete'), ('masina','Masina'), ('matete', 'Matete'), 
        ('lemba', 'Lemba'), ("n'djili", "N'djili"), ('ngaliema', 'Ngaliema'), ('gombe','Gombe')
    ]
    commune = models.CharField(max_length=50, null=True, choices=TYPECOMMUNE)
    service_patient = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.noms 

    class Meta:
        ordering = ['-id']

# ==============================================================================
# 4. FACTURATION ET PRESTATIONS
# ==============================================================================

# ========================================================================================================
# VOTRE MODÈLE PRESTATION (Strictement identique à votre demande)
# ========================================================================================================
class Prestation(models.Model):
    TYPE_CHOICES = [
        ('GLOBAL', 'Général (Fiche, Dossier, Carte)'),
        ('SERVICE', 'Acte de Service (Consultation, Soin)'),
        ('EXTERNE', 'Prestation Externe'),
    ]

    libelle = models.CharField(max_length=150, verbose_name="Nom de la prestation")
    prix_fixe = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (FC/$)")
    
    est_fiche_obligatoire = models.BooleanField(
        default=False, 
        verbose_name="Est la fiche d'entrée ?",
        help_text="Cochez cette case pour la prestation 'Fiche de consultation' unique."
    )

    service = models.ForeignKey(
        'Service', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="prestations",
        verbose_name="Service concerné" ,
        default = 1
    )
    
    type_prestation = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        default='SERVICE'
    )

    active = models.BooleanField(default=True, verbose_name="En vigueur")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Prestation"
        verbose_name_plural = "Prestations"
        constraints = [
            models.UniqueConstraint(
                fields=['est_fiche_obligatoire'], 
                condition=models.Q(est_fiche_obligatoire=True),
                name='unique_fiche_obligatoire'
            )
        ]

    def __str__(self):
        return f"{self.libelle} - {self.prix_fixe}"

# ===============================================================
# FACTURE (CORRIGÉE)
# ================================================================

from decimal import Decimal


# ==================================================================================
# examen 
# ==================================================================================
class Examen(models.Model):
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.prix} $)"
# ==================================================================================
# 5. FLUX MÉDICAL
# ==================================================================================
# 1. DÉFINIR CONSULTATION EN PREMIER
class Consultation(models.Model):
    STATUT_CHOICES = [
        ('TRIAGE', 'En attente de Triage'),
        ('DOCTEUR', 'Prêt pour Consultation'),
        ('LABO', 'Examens en cours'),
        ('ATTENTE_PAIEMENT', 'En attente de Paiement'),
        ('TERMINE', 'Consultation Terminée'),
    ]

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='consultations')
    medecin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultations_medecin')
    infirmier_triage = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='triages_infirmier')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, null=True)
    
    # --- TRIAGE ---
    temperature = models.CharField(max_length=10, null=True, blank=True)
    tension = models.CharField(max_length=20, null=True, blank=True)
    poids = models.CharField(max_length=10, null=True, blank=True)
    pouls = models.CharField(max_length=10, null=True, blank=True)
    date_triage = models.DateTimeField(null=True, blank=True)

    # --- MÉDECIN ---
    diagnostic = models.TextField(null=True, blank=True)
    ordonnance = models.TextField(null=True, blank=True)
    examens_demandes = models.ManyToManyField('Prestation', blank=True)
    est_urgent = models.BooleanField(default=False)
    message_urgence = models.TextField(null=True, blank=True)

    # --- FINANCES ---
    total_a_payer_examens = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    somme_versee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    reste_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paiement_examens_effectue = models.BooleanField(default=False)
    
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='TRIAGE')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_cloture = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calcul automatique du reste
        self.reste_a_payer = self.total_a_payer_examens - self.somme_versee
        
        if self.total_a_payer_examens > 0 and self.reste_a_payer <= 0:
            self.paiement_examens_effectue = True
            if self.statut == 'ATTENTE_PAIEMENT':
                self.statut = 'LABO'
        else:
            self.paiement_examens_effectue = False
            
        super(Consultation, self).save(*args, **kwargs)

    def __str__(self):
        return f"Consultation {self.id} - {self.patient.noms}"


# 2. DÉFINIR FACTURE EN DEUXIÈME
class Facture(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='factures')
    consultation = models.ForeignKey('Consultation', on_delete=models.SET_NULL, null=True, blank=True, related_name='factures_consult')
    prestation = models.ForeignKey('Prestation', on_delete=models.PROTECT)
    
    # Champ de stockage réel du prix
    total_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    date_emission = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_emission']

    def __str__(self):
        return f"FAC-{self.id:04d} | {self.patient.noms}"

    @property
    def total_verse(self):
        # Utilisation du related_name 'paiements' défini dans ton modèle Paiement
        total = self.paiements.aggregate(Sum('montant_verse'))['montant_verse__sum']
        return total or Decimal('0.00')

    @property
    def reste_a_payer(self):
        # On s'assure que total_a_payer n'est jamais None pour le calcul
        dû = self.total_a_payer or Decimal('0.00')
        return max(Decimal('0.00'), dû - self.total_verse)

    @property
    def est_soldee(self):
        return self.reste_a_payer <= 0

    def save(self, *args, **kwargs):
        # --- 1. CALCUL DU PRIX AVANT ENREGISTREMENT ---
        # Priorité 1 : Examens de consultation
        if self.consultation and hasattr(self.consultation, 'total_a_payer_examens') and self.consultation.total_a_payer_examens > 0:
            self.total_a_payer = self.consultation.total_a_payer_examens
        
        # Priorité 2 : Prix fixe de la prestation (Fiche, etc.)
        elif self.total_a_payer == Decimal('0.00') or self.total_a_payer is None:
            if self.prestation:
                self.total_a_payer = self.prestation.prix_fixe

        # Sauvegarde effective de la facture
        super().save(*args, **kwargs)

        # --- 2. DÉBLOCAGE DU FLUX MÉDICAL ---
        # On utilise .update() au lieu de .save() pour éviter la récursion infinie
        if self.est_soldee and self.consultation:
            from .models import Consultation # Import local pour éviter les imports circulaires
            Consultation.objects.filter(id=self.consultation.id).update(
                statut='LABO',
                paiement_examens_effectue=True
            )


# 3. MODÈLE PAIEMENT
class Paiement(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    montant_verse = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    recepteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # On force la mise à jour de la facture pour checker le reste_a_payer
        self.facture.save()
# ==========================================================================
# notification 
# ==========================================================================

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    titre = models.CharField(max_length=100)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)
    service_origine = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.titre} pour {self.user.username}"

# =========================================================================
# presence 
# =========================================================================
class Presence(models.Model):
    # L'employé concerné
    employe = models.ForeignKey(User, on_delete=models.CASCADE, related_name='presences')
    date = models.DateField(default=timezone.now)
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart = models.TimeField(null=True, blank=True)
    # Le réceptionniste qui a validé la présence
    enregistre_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='enregistrements')

    def __str__(self):
        return f"{self.employe.get_full_name()} - {self.date}"

# ===============================================================================
# conge 
# ===============================================================================

class Conge(models.Model):
    TYPES = [('Annuel', 'Annuel'), ('Maladie', 'Maladie'), ('Maternité', 'Maternité')]
    STATUTS = [('En attente', 'En attente'), ('Approuvé', 'Approuvé'), ('Refusé', 'Refusé')]

    employe = models.ForeignKey(User, on_delete=models.CASCADE)
    type_conge = models.CharField(max_length=50, choices=TYPES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    motif = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='En attente')

    def __str__(self):
        return f"Congé {self.employe.username} ({self.statut})"

# ===========================================================================
# categorie
# ===========================================================================
class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
# ===========================================================================
# materiel
# ===========================================================================
class Materiel(models.Model):
    designation = models.CharField(max_length=200)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    quantite_stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=5)  # Pour savoir quand commander
    unite_mesure = models.CharField(max_length=50, default="Pièce") # Boîte, Flacon, etc.

    def __str__(self):
        return self.designation

# ===========================================================================
# mouvementStock
# ===========================================================================
class MouvementStock(models.Model):
    TYPE_MOUVEMENT = (
        ('ENTREE', 'Entrée (Achat/Don)'),
        ('SORTIE', 'Sortie (Utilisation)'),
    )
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE)
    type_mouvement = models.CharField(max_length=10, choices=TYPE_MOUVEMENT)
    quantite = models.IntegerField()
    date_mouvement = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True) # Ex: "Utilisé au bloc opératoire"

    def __str__(self):
        return f"{self.type_mouvement} - {self.materiel.designation}"


# ==================================================================================
# gestion de document hospitalier
# ==================================================================================
class DocumentHospitalier(models.Model):
    TYPE_DOC = [
        ('FACTURE', 'Facture / Reçu'),
        ('RAPPORT', 'Rapport Médical'),
        ('PRESENCE', 'Liste de Présence'),
        ('ORDONNANCE', 'Ordonnance Scannée'),
    ]

    titre = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='documents/%Y/%m/%d/')
    type_document = models.CharField(max_length=20, choices=TYPE_DOC)
    date_creation = models.DateTimeField(auto_now_add=True)
    ajoute_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.type_document} - {self.titre}"

    @property
    def extension(self):
        name, extension = os.path.splitext(self.fichier.name)
        return extension.lower()

# ====================================================================
# transaction 
# ====================================================================
class Transaction(models.Model):
    TYPES_SOURCE = [
        ('CONSULTATION', 'Consultation'),
        ('MORGUE', 'Morgue'),
        ('PHARMACIE', 'Pharmacie'),
        ('LABO', 'Laboratoire'),
    ]
    
    agent = models.ForeignKey(User, on_delete=models.CASCADE) # Pour le lien avec la présence
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=50, choices=TYPES_SOURCE)
    ref_objet = models.PositiveIntegerField() # ID de la facture ou du dossier morgue
    date_heure = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date_heure} - {self.agent.username} - {self.montant}"