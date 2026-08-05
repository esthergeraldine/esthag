"""
views.py — app "projects"

- ProjectListView   → grille (8 projets/page), filtre catégorie, tri,
                       nombre de likes ET état "liké par ce visiteur"
                       calculés dynamiquement (pas de champ à resynchroniser).
- ProjectDetailView → page détail complète.
- toggle_project_like → like / unlike en AJAX, basé sur la session (pas de compte requis).
- submit_project_idea → traite le formulaire de la modale "Proposer une idée".
"""

from django.contrib import messages
from django.db.models import Count, Exists, OuterRef
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView

from ..forms import ProjectIdeaForm
from ..models import Project, ProjectCategory, ProjectChallenge, ProjectLike, Technology


SORT_OPTIONS = {
    "latest": ("-project_date", "Latest First"),
    "oldest": ("project_date", "Oldest First"),
    "popular": ("-likes_total", "Most Liked"),
    "az": ("title", "A → Z"),
}
DEFAULT_SORT = "latest"

# 8 projets par page (voir project_list.html pour la disposition en grille).
PROJECTS_PER_PAGE = 8


def _session_key(request):
    """Garantit qu'une session existe, pour pouvoir tracer les likes anonymes."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


class ProjectListView(ListView):
    model = Project
    template_name = "project_list.html"
    context_object_name = "projects"
    paginate_by = PROJECTS_PER_PAGE

    def get_queryset(self):
        # On s'assure d'avoir une session AVANT de construire la sous-requête
        # "is_liked_by_me", sinon session_key serait None pour un tout premier visiteur.
        session_key = _session_key(self.request)

        liked_subquery = ProjectLike.objects.filter(
            project=OuterRef("pk"), session_key=session_key
        )

        qs = (
            Project.objects.select_related("category")
            .prefetch_related("technologies")
            .annotate(
                likes_total=Count("likes", distinct=True),
                is_liked_by_me=Exists(liked_subquery),
            )
        )

        category_slug = self.request.GET.get("category")
        if category_slug and category_slug != "all":
            qs = qs.filter(category__slug=category_slug)

        sort_key = self.request.GET.get("sort", DEFAULT_SORT)
        order_field, _ = SORT_OPTIONS.get(sort_key, SORT_OPTIONS[DEFAULT_SORT])
        qs = qs.order_by(order_field)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["request"] = self.request

        ctx["categories"] = ProjectCategory.objects.all()
        ctx["current_category"] = self.request.GET.get("category", "all")
        ctx["current_sort"] = self.request.GET.get("sort", DEFAULT_SORT)
        ctx["sort_options"] = SORT_OPTIONS
        ctx["view_mode"] = self.request.GET.get("view", "grid")

        ctx["projects_count"] = Project.objects.count()
        ctx["technologies_count"] = Technology.objects.count()
        ctx["clients_count"] = (
            Project.objects.exclude(client="").values("client").distinct().count()
        )

        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["querystring"] = params.urlencode()

        return ctx


class ProjectDetailView(DetailView):
    model = Project
    template_name = "project_detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object

        ctx["problems"] = project.challenges.filter(kind=ProjectChallenge.PROBLEM)
        ctx["solutions"] = project.challenges.filter(kind=ProjectChallenge.SOLUTION)

        ctx["previous_project"] = (
            Project.objects.filter(project_date__lt=project.project_date)
            .order_by("-project_date")
            .first()
        )
        ctx["next_project"] = (
            Project.objects.filter(project_date__gt=project.project_date)
            .order_by("project_date")
            .first()
        )

        session_key = _session_key(self.request)
        ctx["likes_total"] = project.likes.count()
        ctx["is_liked"] = project.likes.filter(session_key=session_key).exists()
        ctx["idea_form"] = ProjectIdeaForm()

        return ctx


@require_POST
def toggle_project_like(request, pk):
    """Like / unlike en AJAX. Pas de compte requis : basé sur la session du visiteur."""
    project = get_object_or_404(Project, pk=pk)
    session_key = _session_key(request)

    like = ProjectLike.objects.filter(project=project, session_key=session_key).first()
    if like:
        like.delete()
        liked = False
    else:
        ProjectLike.objects.create(project=project, session_key=session_key)
        liked = True

    return JsonResponse({"liked": liked, "likes_count": project.likes.count()})


def submit_project_idea(request, pk):
    """Traite le POST du formulaire (dans la modale) 'Proposer une idée'."""
    project = get_object_or_404(Project, pk=pk)

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    form = ProjectIdeaForm(request.POST)
    if form.is_valid():
        idea = form.save(commit=False)
        idea.project = project
        idea.save()
        messages.success(request, "Merci ! Ton idée a bien été envoyée.")
    else:
        messages.error(request, "Merci de vérifier les champs du formulaire.")

    next_url = request.POST.get("next") or project.get_absolute_url()
    return redirect(next_url)