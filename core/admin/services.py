from django.contrib import admin
from ..models import ServicesIntro, Service, ProcessStep, Technology, FAQItem


class SingletonAdmin(admin.ModelAdmin):
    """N'autorise qu'une seule instance de ce modèle dans l'admin."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ServicesIntro)
class ServicesIntroAdmin(SingletonAdmin):
    pass


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)
    ordering = ("order",)


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)
    ordering = ("order",)



    
    


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question", "order")
    list_editable = ("order",)
    ordering = ("order",)


