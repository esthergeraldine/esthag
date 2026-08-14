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
    path("blog/<slug:slug>/discussion/", views.DiscussionView.as_view(), name="article_discussion"),
    path("blog/<slug:slug>/discussion/stats/", views.discussion_stats, name="discussion_stats"),
    path("blog/<slug:slug>/comments/load/", views.load_comments, name="load_comments"),
    path("blog/<slug:slug>/comments/preview/", views.get_comments_preview, name="comments_preview"),
    path("blog/comment/add/", views.add_comment, name="add_comment"),
    path("blog/comment/<int:comment_id>/reply/", views.add_reply, name="add_reply"),
    path("blog/comment/<int:comment_id>/report/", views.report_comment, name="report_comment"),
    path("blog/comment/<int:comment_id>/like/", views.toggle_comment_like, name="toggle_comment_like"),
    path("blog/comment/<int:comment_id>/replies/", views.load_replies, name="load_replies"),
    path("subscribe/confirm/<str:token>/", views.confirm_subscription, name="confirm_subscription"),
    path("unsubscribe/<str:token>/", views.unsubscribe, name="unsubscribe"),
    path("newsletter/subscribe/", views.subscribe_newsletter, name="subscribe_newsletter"),
    path("projets/", views.ProjectListView.as_view(), name="project_list"),
    path("projets/<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("projets/<int:pk>/proposer-une-idee/", views.submit_project_idea, name="submit_project_idea"),
    path("projets/<int:pk>/like/", views.toggle_project_like, name="toggle_project_like"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("newsletter/", views.newsletter_subscribe, name="newsletter_subscribe"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

