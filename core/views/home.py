from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..models import Service, Article, Project, ArticleSubscriber


def home(request):
    recent_articles = Article.objects.filter(is_published=True).order_by('-published_date')[:6]

    articles_items = [
        {
            "title": article.title,
            "category": article.category.name,
            "excerpt": article.excerpt,
            "img": article.image.url,
            "url": article.get_absolute_url(),
        }
        for article in recent_articles
    ]

    recent_projects = Project.objects.order_by('-project_date')[:4]

    context = {
        "services": Service.objects.all(),
        "articles_items": articles_items,
        "recent_projects": recent_projects,
    }
    return render(request, "home.html", context)


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'success': False, 'message': 'Email requis.'})

    subscriber, created = ArticleSubscriber.objects.get_or_create(email=email)
    if not created:
        if subscriber.is_active:
            return JsonResponse({'success': True, 'message': 'Vous êtes déjà abonné !'})
        subscriber.is_active = True
        subscriber.save()
        return JsonResponse({'success': True, 'message': 'Bienvenue ! Vous êtes abonné.'})

    return JsonResponse({'success': True, 'message': 'Merci pour votre inscription !'})