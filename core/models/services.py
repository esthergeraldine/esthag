# models pour les services, processus de travail, technologies et FAQ
from django.db import models

# Create your models here.from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse




class ServicesIntro(models.Model):
    """En-tête de la page Services (une seule instance)."""
    title_script = models.CharField(
        max_length=100, default="Nos Services", verbose_name="Titre manuscrit"
    )
    subtitle = models.CharField(
        max_length=255, blank=True,
        default="Ce que je peux faire pour vous",
        verbose_name="Sous-titre",
    )
    description = models.TextField(
        blank=True, default="", verbose_name="Texte d'introduction"
    )

    class Meta:
        verbose_name = "Intro Services"
        verbose_name_plural = "Intro Services"

    def __str__(self):
        return "En-tête page Services"

    def save(self, *args, **kwargs):
        # Une seule instance possible.
        self.pk = 1
        super().save(*args, **kwargs)


class Service(models.Model):
    """Une prestation, affichée dans la section « Prestations »."""
    title = models.CharField(max_length=120, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    icon = models.ImageField(
        upload_to="services/icons/", blank=True, null=True,
        verbose_name="Icône / image",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    image_1 = models.ImageField(
       upload_to="services/approach/", blank=True, null=True,
       help_text="Petite photo au premier plan (bas-gauche de la galerie)"
   )
    image_2 = models.ImageField(
       upload_to="services/approach/", blank=True, null=True,
       help_text="Grande photo en arrière-plan (haut-droite de la galerie)"
   )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Prestation"
        verbose_name_plural = "Prestations"

    def __str__(self):
        return self.title


class ProcessStep(models.Model):
    """Une étape, affichée dans la section « Processus de travail »."""
    title = models.CharField(max_length=120, verbose_name="Titre de l'étape")
    description = models.TextField(verbose_name="Description")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Étape du processus"
        verbose_name_plural = "Processus de travail"

    def __str__(self):
        return self.title





class FAQItem(models.Model):
    """Une question / réponse, affichée dans la section « FAQ »."""
    question = models.CharField(max_length=255, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Question (FAQ)"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.question
    
    
    
    
    