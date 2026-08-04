from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path("services/", views.services, name="services"),
    path('contact/', views.contact, name='contact'),
    path("blog/", views.ArticleListView.as_view(), name="article_list"),
    path("blog/<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("projets/", views.ProjectListView.as_view(), name="project_list"),
    path("projets/<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("projets/<int:pk>/proposer-une-idee/", views.submit_project_idea, name="submit_project_idea"),
    path("projets/<int:pk>/like/", views.toggle_project_like, name="toggle_project_like"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

