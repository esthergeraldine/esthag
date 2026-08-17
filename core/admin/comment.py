from django.contrib import admin
from django.utils.html import format_html

from ..models.comment import Comment, CommentLike, ReportedComment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'display_name_admin',
        'article',
        'status_badge',
        'likes_count',
        'replies_count',
        'created_date',
    )
    list_filter = ('status', 'created_date', 'article__category')
    search_fields = ('name', 'email', 'content', 'article__title')
    actions = ['mark_as_spam', 'hide_comments', 'publish_comments']

    fieldsets = (
        ('Contenu', {
            'fields': ('article', 'parent', 'subscriber', 'name', 'email', 'content')
        }),
        ('Statut', {
            'fields': ('status', 'likes_count', 'replies_count')
        }),
        ('Dates', {
            'fields': ('created_date', 'updated_date')
        }),
    )

    readonly_fields = ('created_date', 'updated_date', 'likes_count', 'replies_count')

    def display_name_admin(self, obj):
        return obj.display_name
    display_name_admin.short_description = 'Nom'

    def status_badge(self, obj):
        colors = {
            'published': 'green',
            'hidden': 'orange',
            'spam': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: #{0}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px;">{1}</span>',
            '22c55e' if color == 'green' else ('f97316' if color == 'orange' else 'ef4444'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    @admin.action(description='Marquer comme spam')
    def mark_as_spam(self, request, queryset):
        queryset.update(status='spam')

    @admin.action(description='Masquer les commentaires')
    def hide_comments(self, request, queryset):
        queryset.update(status='hidden')

    @admin.action(description='Publier les commentaires')
    def publish_comments(self, request, queryset):
        queryset.update(status='published')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('comment', 'session_key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('comment__name', 'session_key')


@admin.register(ReportedComment)
class ReportedCommentAdmin(admin.ModelAdmin):
    list_display = ('comment', 'reason_badge', 'session_key', 'created_at')
    list_filter = ('reason', 'created_at')
    search_fields = ('comment__name', 'comment__content', 'session_key')
    actions = ['mark_as_spam', 'hide_comment', 'dismiss_reports']

    def reason_badge(self, obj):
        colors = {
            'spam': 'red',
            'inappropriate': 'orange',
            'harassment': 'purple',
            'other': 'gray',
        }
        color = colors.get(obj.reason, 'gray')
        return format_html(
            '<span style="background-color: #{0}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px;">{1}</span>',
            'ef4444' if color == 'red' else ('f97316' if color == 'orange' else ('a855f7' if color == 'purple' else '6b7280')),
            obj.get_reason_display()
        )
    reason_badge.short_description = 'Motif'

    @admin.action(description='Marquer le commentaire comme spam')
    def mark_as_spam(self, request, queryset):
        for report in queryset:
            report.comment.status = 'spam'
            report.comment.save()
        queryset.delete()

    @admin.action(description='Masquer le commentaire')
    def hide_comment(self, request, queryset):
        for report in queryset:
            report.comment.status = 'hidden'
            report.comment.save()
        queryset.delete()

    @admin.action(description='Ignorer les signalements')
    def dismiss_reports(self, request, queryset):
        queryset.delete()
