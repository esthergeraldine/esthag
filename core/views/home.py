from django.shortcuts import render
from django.http import JsonResponse

from ..models import Service, Project


def home(request):
    featured_projects = Project.objects.all()[:3]

    context = {
        "featured_projects": featured_projects,
        "services": Service.objects.all(),
    }
    return render(request, "home.html", context)


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        return JsonResponse({'success': True, 'message': 'Merci pour votre inscription !'})
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})