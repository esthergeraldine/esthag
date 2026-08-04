#  // services viewfrom django.shortcuts import render
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render


from .models import FAQItem, ProcessStep, Service, ServicesIntro, Technology


# pour gerer les projets 
from django.contrib import messages

 
def services(request):
    context = {
        "intro": ServicesIntro.objects.first(),
        "services_list": Service.objects.all(),
        "process_steps": ProcessStep.objects.all(),
        "technologies": Technology.objects.all(),
        "faq_items": FAQItem.objects.all(),
    }
    return render(request, "services.html", context)


