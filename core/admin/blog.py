"""
Admin pour l'application blog de TechSpace.
À placer dans blog/admin.py
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db import models

from django_ckeditor_5.widgets import CKEditor5Widget

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

    formfield_overrides = {
        models.TextField: {
            "widget": CKEditor5Widget(
                attrs={
                    "data-language": "fr",
                    "style": "min-height: 500px;",
                }
            )
        },
    }

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
    list_display = ("email", "name", "status_badge", "confirmed_at", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("email", "name")
    readonly_fields = ("confirmation_token", "token_expires_at", "unsubscribe_token", "confirmed_at", "created_at")

    fieldsets = (
        ("Abonné", {
            "fields": ("email", "name", "status")
        }),
        ("Confirmation", {
            "fields": ("confirmation_token", "token_expires_at", "confirmed_at")
        }),
        ("Désabonnement", {
            "fields": ("unsubscribe_token",)
        }),
        ("Dates", {
            "fields": ("created_at",)
        }),
    )

    actions = ["confirm_subscribers", "unsubscribe_subscribers"]

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'unsubscribed': 'red',
        }
        color = colors.get(obj.status, 'gray')
        color_hex = {'orange': 'f97316', 'green': '22c55e', 'red': 'ef4444'}.get(color, '6b7280')
        return format_html(
            '<span style="background-color: #{0}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px;">{1}</span>',
            color_hex,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    @admin.action(description="Confirmer les abonnés sélectionnés")
    def confirm_subscribers(self, request, queryset):
        for subscriber in queryset.filter(status='pending'):
            subscriber.confirm()

    @admin.action(description="Désabonner les abonnés sélectionnés")
    def unsubscribe_subscribers(self, request, queryset):
        queryset.update(status='unsubscribed')