"""
Modèles pour l'application blog de TechSpace.
À placer dans blog/models.py (adapte le nom de l'app si besoin).
"""

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


class Category(models.Model):
    """
    Catégories utilisées pour filtrer les articles
    (Web Development, Design, Productivity, Lifestyle, Career, Inspiration...)
    et pour la sidebar "Catégories" avec compteur d'articles.
    """
    name = models.CharField("Nom", max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    order = models.PositiveIntegerField("Ordre d'affichage", default=0)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:article_list") + f"?category={self.slug}"


class Author(models.Model):
    """
    Auteur de l'article, affiché dans le header ("Par Marie Dupont")
    et dans le bloc "À propos de l'auteure" en bas de la page de détail.
    Pourra plus tard être fusionné avec le modèle Profile de la page About.
    """
    name = models.CharField("Nom", max_length=100)
    email = models.EmailField("Email", blank=True)
    bio = models.TextField("Bio courte", blank=True)
    photo = models.ImageField("Photo", upload_to="blog/authors/", blank=True, null=True)
    website = models.URLField("Site web", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    github = models.URLField("GitHub", blank=True)
    dribbble = models.URLField("Dribbble", blank=True)

    class Meta:
        verbose_name = "Auteur"
        verbose_name_plural = "Auteurs"

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Article de blog. Couvre la hero section, les cartes de la grille,
    et la page de détail (image principale, citation en avant, navigation
    article précédent/suivant, articles récents de la sidebar).
    """
    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    category = models.ForeignKey(
        Category, related_name="articles",
        on_delete=models.PROTECT, verbose_name="Catégorie"
    )
    author = models.ForeignKey(
        Author, related_name="articles",
        on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Auteur"
    )

    excerpt = models.CharField(
        "Extrait / description courte", max_length=300,
        help_text="Affiché sur la carte de la liste des articles."
    )
    content = CKEditor5Field("Contenu")
    featured_quote = models.CharField(
        "Citation mise en avant", max_length=300, blank=True,
        help_text='Ex : "Le design n\'est pas juste ce à quoi ça ressemble..."'
    )
    featured_quote_author = models.CharField(
        "Auteur de la citation", max_length=100, blank=True,
        help_text='Ex : "Steve Jobs". Laisser vide si la citation est de toi.'
    )

    image = models.ImageField(
        "Image principale", upload_to="blog/articles/",
        help_text="Utilisée dans la hero de la page de détail et la carte de la liste."
    )

    reading_time = models.PositiveIntegerField(
        "Temps de lecture (minutes)", default=5
    )

    is_featured = models.BooleanField(
        "Article à la une", default=False,
        help_text='Affiché dans le widget "Featured Post" de la sidebar.'
    )
    is_published = models.BooleanField("Publié", default=True)

    views_count = models.PositiveIntegerField("Vues", default=0)

    published_date = models.DateTimeField("Date de publication", default=timezone.now)
    updated_date = models.DateTimeField("Dernière modification", auto_now=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-published_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            i = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug": self.slug})

    @property
    def reading_time_display(self):
        return f"{self.reading_time} min de lecture"

    def get_previous_article(self):
        return Article.objects.filter(
            is_published=True,
            published_date__lt=self.published_date
        ).order_by("-published_date").first()

    def get_next_article(self):
        return Article.objects.filter(
            is_published=True,
            published_date__gt=self.published_date
        ).order_by("published_date").first()


class ArticleLike(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="likes")
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "session_key")

    def __str__(self):
        return f"Like — {self.article}"


class ArticleSubscriber(models.Model):
    STATUS_CHOICES = (
        ("pending", "En attente"),
        ("confirmed", "Confirmé"),
        ("unsubscribed", "Désabonné"),
    )

    email = models.EmailField("Email", unique=True)
    name = models.CharField("Nom", max_length=100)
    status = models.CharField(
        "Statut",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    confirmation_token = models.CharField("Token de confirmation", max_length=64, blank=True)
    token_expires_at = models.DateTimeField("Expiration du token", null=True, blank=True)
    unsubscribe_token = models.CharField("Token de désabonnement", max_length=64, blank=True)
    confirmed_at = models.DateTimeField("Confirmé le", null=True, blank=True)
    created_at = models.DateTimeField("Créé le", default=timezone.now)

    class Meta:
        verbose_name = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.unsubscribe_token:
            import secrets
            self.unsubscribe_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def generate_confirmation_token(self):
        import secrets
        from django.utils import timezone
        self.confirmation_token = secrets.token_urlsafe(32)
        self.token_expires_at = timezone.now() + timezone.timedelta(days=2)
        self.save(update_fields=["confirmation_token", "token_expires_at"])
        return self.confirmation_token

    def confirm(self):
        from django.utils import timezone
        self.status = "confirmed"
        self.confirmed_at = timezone.now()
        self.confirmation_token = ""
        self.token_expires_at = None
        self.save(update_fields=["status", "confirmed_at", "confirmation_token", "token_expires_at"])

    def unsubscribe(self):
        self.status = "unsubscribed"
        self.save(update_fields=["status"])

    def is_confirmed(self):
        return self.status == "confirmed"

    @property
    def is_active(self):
        return self.status == "confirmed"
