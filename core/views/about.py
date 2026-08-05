from django.shortcuts import render


from ..models import Quality, TimelineEntry


def about(request):
    context = {
        "qualities": Quality.objects.all()[:4],
        "education": TimelineEntry.objects.filter(type="education"),
        "experience": TimelineEntry.objects.filter(type="experience"),
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