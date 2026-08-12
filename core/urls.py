from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path("services/", views.services, name="services"),
    path("blog/", views.ArticleListView.as_view(), name="article_list"),
    path("blog/search/", views.search_articles, name="article_search"),
    path("blog/<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("blog/<slug:slug>/like/", views.toggle_article_like, name="toggle_article_like"),
    path("blog/<slug:slug>/comment/", views.add_article_comment, name="add_article_comment"),
    path("blog/comment/<int:comment_id>/like/", views.toggle_comment_like, name="toggle_comment_like"),
    path("projets/", views.ProjectListView.as_view(), name="project_list"),
    path("projets/<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("projets/<int:pk>/proposer-une-idee/", views.submit_project_idea, name="submit_project_idea"),
    path("projets/<int:pk>/like/", views.toggle_project_like, name="toggle_project_like"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("newsletter/", views.newsletter_subscribe, name="newsletter_subscribe"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

