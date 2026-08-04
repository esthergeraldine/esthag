from django.contrib import admin
from .models import Quality, TimelineEntry


@admin.register(Quality)
class QualityAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)
    ordering = ("order",)


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "year", "order")
    list_filter = ("type",)
    list_editable = ("order",)
    ordering = ("type", "order")