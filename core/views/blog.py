"""
Vues pour l'application blog de TechSpace.
À placer dans blog/views.py
"""

from django.db.models import Count, Q, F, Exists, OuterRef
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from ..models import Article, Category, ArticleLike, ArticleSubscriber


def _session_key(request):
    """Garantit qu'une session existe."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


class ArticleListView(ListView):
    """
    Page de liste des articles :
    - filtre par catégorie (?category=slug)
    - recherche full-text simple (?q=...)
    - pagination dynamique, 6 articles par page
    - sidebar : catégories + compteur, featured post, recherche
    """
    model = Article
    template_name = "blog_list.html"
    context_object_name = "articles"
    paginate_by = 6

    def get_queryset(self):
        session_key = _session_key(self.request)
        liked_subquery = ArticleLike.objects.filter(article=OuterRef("pk"), session_key=session_key)

        queryset = Article.objects.filter(is_published=True).select_related(
            "category", "author"
        ).annotate(
            likes_total=Count("likes", distinct=True),
            is_liked_by_me=Exists(liked_subquery),
        )

        category_slug = self.request.GET.get("category")
        if category_slug and category_slug != "all":
            queryset = queryset.filter(category__slug=category_slug)

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(excerpt__icontains=query)
                | Q(content__icontains=query)
            )

        sort = self.request.GET.get("sort", "newest")
        if sort == "oldest":
            queryset = queryset.order_by("published_date")
        elif sort == "popular":
            queryset = queryset.order_by("-views_count")
        else:
            queryset = queryset.order_by("-published_date")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request

        context["categories"] = Category.objects.annotate(
            article_count=Count("articles", filter=Q(articles__is_published=True))
        ).order_by("order", "name")

        context["current_category"] = self.request.GET.get("category", "all")
        context["search_query"] = self.request.GET.get("q", "")
        context["current_sort"] = self.request.GET.get("sort", "newest")

        context["featured_post"] = (
            Article.objects.filter(is_published=True, is_featured=True)
            .order_by("-published_date")
            .first()
        )

        # Stats pour la hero section
        context["articles_count"] = Article.objects.filter(is_published=True).count()
        context["categories_count"] = Category.objects.count()
        context["subscribers_count"] = ArticleSubscriber.objects.filter(status='confirmed').count()

        params = self.request.GET.copy()
        params.pop("page", None)
        context["querystring"] = params.urlencode()

        return context


class ArticleDetailView(DetailView):
    """
    Page de détail d'un article :
    - grande image = article.image
    - navigation article précédent / suivant
    - sidebar : à propos de l'article, articles récents, catégories
    """
    model = Article
    template_name = "blog_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related(
            "category", "author"
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Incrémente le compteur de vues sans déclencher de race condition
        Article.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object

        session_key = _session_key(self.request)
        liked_subquery = ArticleLike.objects.filter(article=OuterRef("pk"), session_key=session_key)

        article_qs = Article.objects.annotate(
            likes_total=Count("likes", distinct=True),
            is_liked_by_me=Exists(liked_subquery),
        )

        context["previous_article"] = article.get_previous_article()
        context["next_article"] = article.get_next_article()

        same_category = Article.objects.filter(
            is_published=True,
            category=article.category
        ).exclude(pk=article.pk).order_by("-published_date")[:3]

        if same_category.count() < 3:
            exclude_ids = list(same_category.values_list('pk', flat=True)) + [article.pk]
            other_articles = (
                Article.objects.filter(is_published=True)
                .exclude(pk__in=exclude_ids)
                .order_by("-likes__created_at", "-comments__created_date")[:3 - same_category.count()]
            )
            recommendations = list(same_category) + list(other_articles)
        else:
            recommendations = list(same_category)

        context["recommendations"] = recommendations

        context["categories"] = Category.objects.annotate(
            article_count=Count("articles", filter=Q(articles__is_published=True))
        ).order_by("order", "name")

        context["total_articles"] = Article.objects.filter(is_published=True).count()

        article_likes_qs = article_qs.filter(pk=article.pk)
        context["likes_total"] = article_likes_qs.first().likes_total
        context["is_liked"] = article_likes_qs.first().is_liked_by_me

        context["total_comments_count"] = article.comments.filter(status='published', parent=None).count()

        comments_qs = article.comments.filter(status='published', parent=None).select_related('subscriber')
        if comments_qs.exists():
            best_comment = comments_qs.order_by('-likes_count', '-created_date').first()
            context["preview_comment"] = {
                'name': best_comment.display_name,
                'content': best_comment.content[:150] + '...' if len(best_comment.content) > 150 else best_comment.content,
                'likes_count': best_comment.likes_count,
            }
        else:
            context["preview_comment"] = None

        return context


@require_POST
def toggle_article_like(request, slug):
    """Like / unlike un article en AJAX."""
    article = get_object_or_404(Article, slug=slug)
    session_key = _session_key(request)

    like = ArticleLike.objects.filter(article=article, session_key=session_key).first()
    if like:
        like.delete()
        liked = False
    else:
        ArticleLike.objects.create(article=article, session_key=session_key)
        liked = True

    return JsonResponse({"liked": liked, "likes_count": article.likes.count()})


def search_articles(request):
    """Recherche AJAX pour articles."""
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "all")

    if len(query) < 2:
        return JsonResponse({"query": query, "total": 0, "results": []})

    queryset = Article.objects.filter(
        is_published=True
    ).select_related("category", "author").filter(
        Q(title__icontains=query)
        | Q(excerpt__icontains=query)
        | Q(content__icontains=query)
        | Q(category__name__icontains=query)
        | Q(author__name__icontains=query)
    )

    if category and category != "all":
        queryset = queryset.filter(category__slug=category)

    articles = queryset.order_by("-published_date")[:20]

    results = [
        {
            "slug": a.slug,
            "title": a.title,
            "excerpt": a.excerpt,
            "category": a.category.name,
            "category_slug": a.category.slug,
            "reading_time": a.reading_time,
            "url": a.get_absolute_url(),
            "image": a.image.url if a.image else None,
        }
        for a in articles
    ]

    return JsonResponse({"query": query, "total": len(results), "results": results})