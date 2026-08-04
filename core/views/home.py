from django.shortcuts import render
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import About, BlogIntro, Category, Post
from .models import FAQItem, ProcessStep, Service, ServicesIntro, Technology
from .models import Project
from .models import Quality, TimelineEntry 

# pour gerer les projets 
from django.contrib import messages
from django.views.generic import ListView, DetailView
from .forms import ProjectIdeaForm
from .models import Category, Project, ProjectChallenge, Technology



def home(request):
    featured_projects = Project.objects.filter(is_featured=True)[:3]

    # Si tu n'as pas encore marqué de projets en "featured", cette ligne
    # prend simplement les 3 derniers projets publiés à la place :
    if not featured_projects:
        featured_projects = Project.objects.all()[:3]

    context = {
        "about": About.objects.first(),
        "featured_projects": featured_projects,
        "services": Service.objects.all(), 
        
    }
    return render(request, "home.html", context)