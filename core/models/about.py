# Create your models here.from django.db import models
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse





class Quality(models.Model):
    """
    Les 4 cartes qualités affichées autour de la photo, en haut de la
    page À propos. Garde exactement 4 entrées actives pour que la mise
    en page circulaire (haut-gauche / haut-droite / bas-gauche /
    bas-droite) reste cohérente.
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(
        max_length=50,
        default="fa-solid fa-check",
        help_text="Classe d'icône Font Awesome, ex: fa-solid fa-lightbulb, fa-solid fa-comments",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Qualité"
        verbose_name_plural = "Qualités (header À propos)"

    def __str__(self):
        return self.title


class TimelineEntry(models.Model):
    """
    Une entrée de parcours académique OU d'expérience professionnelle.
    Le champ "type" distingue les deux sections de la page À propos.
    """

    TYPE_CHOICES = [
        ("education", "Parcours académique"),
        ("experience", "Expérience professionnelle"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    year = models.CharField(max_length=50, help_text="Ex: 2022 — 2024")
    title = models.CharField(max_length=200, help_text="Diplôme obtenu ou intitulé du poste")
    subtitle = models.CharField(
        max_length=200, blank=True,
        help_text="École / université, ou nom de l'entreprise"
    )
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        default="fa-solid fa-graduation-cap",
        help_text="Classe d'icône Font Awesome, ex: fa-solid fa-graduation-cap, fa-solid fa-briefcase",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage (0 = en premier, généralement du plus ancien au plus récent)",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Entrée de parcours"
        verbose_name_plural = "Parcours & expérience"

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"



