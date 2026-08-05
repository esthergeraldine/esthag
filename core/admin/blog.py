"""
Admin pour l'application blog de TechSpace.
À placer dans blog/admin.py
"""

from django.contrib import admin
from ..models import Category, Author, Article


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
        "likes_count",
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
            "fields": ("is_featured", "is_published", "views_count", "likes_count")
        }),
    )