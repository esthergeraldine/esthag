from django.shortcuts import render
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render


from .models import Quality, TimelineEntry ,About

# pour gerer les projets 
from django.contrib import messages



def about(request):
    """
    Vue de la page "À propos" du portfolio TechSpace.
    Qualities, education et experience viennent maintenant de la BDD
    (modifiables depuis /admin/) au lieu de listes codées en dur.
    """
    context = {
        "about": About.objects.first(),
        "qualities": Quality.objects.all()[:4],
        "education": TimelineEntry.objects.filter(type="education"),
        "experience": TimelineEntry.objects.filter(type="experience"),
        # skills et tools restent des listes simples pour l'instant :
        # dis-moi si tu veux qu'elles deviennent aussi des modèles admin.
        "skills": [
            {"name": "HTML / CSS / Tailwind", "level": 95},
            {"name": "JavaScript", "level": 85},
            {"name": "Django / Python", "level": 80},
            {"name": "UI / UX Design", "level": 90},
            {"name": "Figma", "level": 88},
            {"name": "SEO & Performance", "level": 75},
        ],
        "tools": [
            "Figma", "Tailwind CSS", "Django", "JavaScript",
            "Git & GitHub", "VS Code", "Photoshop", "Notion",
        ],
    }
    return render(request, "about.html", context)


# N'oublie pas d'importer les modèles en haut de views.py :
#   from .models import Quality, TimelineEntry