from django.shortcuts import render
from django.http import JsonResponse

from ..models import Service, Article


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

    context = {
        "services": Service.objects.all(),
        "articles_items": articles_items,
    }
    return render(request, "home.html", context)


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        return JsonResponse({'success': True, 'message': 'Merci pour votre inscription !'})
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})