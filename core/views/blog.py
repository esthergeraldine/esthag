"""
Vues pour l'application blog de TechSpace.
À placer dans blog/views.py
"""

from django.db.models import Count, Q, F
from django.views.generic import ListView, DetailView

from .models import Article, Category


class ArticleListView(ListView):
    """
    Page de liste des articles :
    - filtre par catégorie (?category=slug)
    - recherche full-text simple (?q=...)
    - pagination dynamique, 6 articles par page
    - sidebar : catégories + compteur, featured post, recherche
    """
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 6

    def get_queryset(self):
        queryset = Article.objects.filter(is_published=True).select_related(
            "category", "author"
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

        # Conserve les filtres actifs (catégorie, recherche, tri) dans les liens
        # de pagination, sans le paramètre "page" lui-même.
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
    template_name = "blog/article_detail.html"
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

        context["previous_article"] = article.get_previous_article()
        context["next_article"] = article.get_next_article()

        context["recent_articles"] = (
            Article.objects.filter(is_published=True)
            .exclude(pk=article.pk)
            .order_by("-published_date")[:3]
        )

        context["categories"] = Category.objects.annotate(
            article_count=Count("articles", filter=Q(articles__is_published=True))
        ).order_by("order", "name")

        context["total_articles"] = Article.objects.filter(is_published=True).count()

        return context