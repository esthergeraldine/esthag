"""
Admin pour l'application blog de TechSpace.
À placer dans blog/admin.py
"""

from django.contrib import admin
from ..models import Category, Author, Article, ArticleSubscriber


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "linkedin", "github")
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "author",
        "published_date",
        "is_featured",
        "is_published",
        "views_count",
    )
    list_filter = ("category", "author", "is_featured", "is_published")
    list_editable = ("is_featured", "is_published")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_date"
    readonly_fields = ("views_count", "updated_date")

    fieldsets = (
        ("Contenu", {
            "fields": ("title", "slug", "category", "author", "image")
        }),
        ("Texte", {
            "fields": ("excerpt", "content", "featured_quote", "featured_quote_author")
        }),
        ("Métadonnées", {
            "fields": ("reading_time", "published_date", "updated_date")
        }),
        ("Statut & statistiques", {
            "fields": ("is_featured", "is_published", "views_count")
        }),
    )


@admin.register(ArticleSubscriber)
class ArticleSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    actions = ["activate_subscribers", "deactivate_subscribers"]

    @admin.action(description="Activer les abonnés sélectionnés")
    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Désactiver les abonnés sélectionnés")
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)