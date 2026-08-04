"""
models.py — app "projects"

Couvre :
  - la grille de la page liste (badges de statut, likes, technos avec icône,
    date, taille d'équipe, catégories de filtre)
  - la page détail façon "Estha" (rôle, durée, année, aperçus/screenshots,
    "Key Features", "The Impact", témoignage, technologies utilisées)
  - la nouvelle section "Problèmes & Solutions" (2 colonnes, dynamique)
  - le bouton "Proposer une idée" (stocke la suggestion en base)

Tout ce qui est répétable (features, screenshots, stats, problèmes/solutions)
est un modèle à part relié par ForeignKey, géré comme un "inline" dans
l'admin Django → tu ajoutes/retires une ligne dans l'admin, la page se
met à jour automatiquement, sans toucher au code.
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# ------------------------------------------------------------------
# Catégories (onglets de filtre : "Web Development", "Mobile Apps"...)
# Nommée "ProjectCategory" (et pas juste "Category") pour ne jamais
# entrer en collision avec la Category de ton app blog.
# ------------------------------------------------------------------
class ProjectCategory(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ------------------------------------------------------------------
# Technologies (icône + nom, ex : Django, React, Tailwind CSS...)
# ------------------------------------------------------------------
class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    # logo de la techno (png/svg) affiché dans les pastilles
    icon = models.ImageField(upload_to="technologies/icons/", blank=True, null=True)
    # couleur de secours si aucune icône n'est fournie (ex: "#3776AB" pour Python)
    fallback_color = models.CharField(max_length=7, default="#A8536A")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ------------------------------------------------------------------
# Projet principal
# ------------------------------------------------------------------
class Project(models.Model):
    STATUS_PRODUCTION = "production"
    STATUS_DEVELOPMENT = "development"
    STATUS_PROTOTYPE = "prototype"
    STATUS_CHOICES = [
        (STATUS_PRODUCTION, "En production"),
        (STATUS_DEVELOPMENT, "En développement"),
        (STATUS_PROTOTYPE, "Prototype"),
    ]
    # NB : les couleurs du badge de statut sont écrites en dur dans le
    # template (project_list.html) avec un {% if %}/{% elif %}, plutôt
    # que générées ici en Python. Raison : Tailwind ne scanne que les
    # fichiers .html/.js pour savoir quelles classes générer — une classe
    # construite dans un fichier .py (comme "bg-secondary/15 text-secondary")
    # n'est jamais vue par le JIT et se retrouve donc sans aucun style
    # (c'est ce qui rendait le badge invisible).

    # ---- Contenu principal ----
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    short_description = models.CharField(
        max_length=250, help_text="Résumé affiché sur la carte et en haut de la page détail."
    )
    description = models.TextField(help_text="Texte complet, section « About the Project ».")

    category = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL, null=True, related_name="projects"
    )
    technologies = models.ManyToManyField(Technology, related_name="projects", blank=True)

    # ---- Statut / engagement ----
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DEVELOPMENT)
    # Le nombre de likes n'est plus un compteur statique (risque de désync) :
    # il se calcule dynamiquement depuis la relation ProjectLike, voir plus bas.

    # ---- Méta affichées dans la carte et le détail ----
    client = models.CharField(max_length=100, blank=True, help_text="Laisser vide si projet personnel.")
    role = models.CharField(max_length=100, blank=True, help_text='Ex : "Full Stack Developer"')
    duration = models.CharField(max_length=50, blank=True, help_text='Ex : "3 Months"')
    project_date = models.DateField(help_text="Sert à afficher le mois/année (carte) et l'année (détail).")
    team_size = models.PositiveIntegerField(
        null=True, blank=True, help_text="Laisser vide pour afficher « Projet personnel »."
    )

    # ---- Images ----
    thumbnail = models.ImageField(
        upload_to="projects/thumbnails/", help_text="Image affichée sur la carte, dans la grille."
    )
    hero_image = models.ImageField(
        upload_to="projects/hero/", blank=True, null=True,
        help_text="Grand visuel/mockup en haut de la page détail (optionnel, sinon thumbnail est réutilisée)."
    )

    # ---- Liens ----
    live_url = models.URLField(blank=True)
    repo_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-project_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"pk": self.pk})

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def team_display(self):
        return f"Équipe de {self.team_size}" if self.team_size else "Projet personnel"

    @property
    def display_image(self):
        return self.hero_image or self.thumbnail


# ------------------------------------------------------------------
# Likes — un visiteur (identifié par sa session, pas besoin de compte)
# peut liker/déliker un projet. Le nombre affiché = COUNT() dynamique
# sur cette table, jamais un champ à resynchroniser manuellement.
# ------------------------------------------------------------------
class ProjectLike(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="likes")
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "session_key")

    def __str__(self):
        return f"Like — {self.project}"


# ------------------------------------------------------------------
# "Key Features" — page détail
# ------------------------------------------------------------------
class ProjectFeature(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="features")
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


# ------------------------------------------------------------------
# "Project Preview" / "Project Screenshots" — carrousel horizontal
# ------------------------------------------------------------------
class ProjectScreenshot(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="screenshots")
    image = models.ImageField(upload_to="projects/screenshots/")
    caption = models.CharField(
        max_length=80, blank=True, help_text='Petit titre affiché sur la vignette, ex : "Lessons".'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"Screenshot #{self.pk}"


# ------------------------------------------------------------------
# "The Impact" — stats libres (Active Users, Completion Rate, Rating...)
# ------------------------------------------------------------------
class ProjectStat(models.Model):
    ICON_CHOICES = [
        ("users", "Utilisateurs"),
        ("trending-up", "Progression"),
        ("star", "Note / étoile"),
        ("clock", "Temps"),
        ("check", "Validation"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="stats")
    label = models.CharField(max_length=60, help_text='Ex : "Active Users"')
    value = models.CharField(max_length=30, help_text='Ex : "2K+", "85%", "4.9 / 5"')
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default="check")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.label} — {self.value}"


# ------------------------------------------------------------------
# Témoignage client (bloc citation à droite de "The Impact")
# ------------------------------------------------------------------
class ProjectTestimonial(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="testimonial")
    quote = models.TextField()
    author_name = models.CharField(max_length=80)
    author_role = models.CharField(max_length=80, blank=True)
    author_avatar = models.ImageField(upload_to="projects/testimonials/", blank=True, null=True)

    def __str__(self):
        return f"Témoignage — {self.author_name}"


# ------------------------------------------------------------------
# "Problèmes & Solutions" — section 2 colonnes, dynamique
# ------------------------------------------------------------------
class ProjectChallenge(models.Model):
    PROBLEM = "problem"
    SOLUTION = "solution"
    KIND_CHOICES = [
        (PROBLEM, "Problème"),
        (SOLUTION, "Solution"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="challenges")
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    text = models.CharField(max_length=250)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["kind", "order", "id"]

    def __str__(self):
        return f"[{self.get_kind_display()}] {self.text[:40]}"


# ------------------------------------------------------------------
# "Proposer une idée" — suggestions envoyées depuis la carte projet
# ------------------------------------------------------------------
class ProjectIdea(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="idea_suggestions", null=True, blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Idée de {self.name} — {self.project}"