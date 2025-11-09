from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Categorie(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)

    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categories"


    def __str__(self):
        return self.name

class Ad(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='ad_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='ads/', null=True, blank=True)
    image3 = models.ImageField(upload_to='ads/', null=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='ads')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
