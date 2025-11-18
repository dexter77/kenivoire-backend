from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Categorie(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default="📦")

    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Ad(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ads'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='ad_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='ad_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='ad_images/', blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255)
    premium = models.BooleanField(default=False)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ads'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    # 🔹 Champs spécifiques aux véhicules
    annee_mise_en_circulation = models.PositiveIntegerField(null=True, blank=True)
    kilometrage = models.PositiveIntegerField(null=True, blank=True)
    annee_modele = models.PositiveIntegerField(null=True, blank=True)
    marque = models.CharField(max_length=100, null=True, blank=True)
    carburant = models.CharField(
        max_length=50,
        choices=[
            ('essence', 'Essence'),
            ('diesel', 'Diesel'),
            ('electrique', 'Électrique'),
            ('hybride', 'Hybride'),
        ],
        null=True,
        blank=True
    )
    transmission = models.CharField(
        max_length=50,
        choices=[
            ('manuelle', 'Manuelle'),
            ('automatique', 'Automatique'),
        ],
        null=True,
        blank=True
    )

    # 🏠 Champs spécifiques à l’immobilier
    type_offre = models.CharField(
        max_length=20,
        choices=[
            ('location', 'Location'),
            ('vente', 'Vente'),
        ],
        null=True,
        blank=True,
        help_text="Spécifie si le bien est en vente ou en location"
    )
    superficie = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Superficie du bien en m²"
    )
    zone = models.CharField(max_length=100, null=True, blank=True)
    nombre_pieces = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
