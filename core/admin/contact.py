"""
contact/admin.py
"""
from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["subject", "name", "email", "created_at", "is_read", "email_sent"]
    list_editable = ["is_read"]
    list_filter = ["is_read", "email_sent", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["name", "email", "subject", "message", "created_at", "email_sent"]
    ordering = ["-created_at"]