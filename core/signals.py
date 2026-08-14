from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Article, ArticleSubscriber


class ArticleNotificationSent(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='notification_sent')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification d'article envoyée"
        verbose_name_plural = "Notifications d'articles envoyées"


@receiver(pre_save, sender=Article)
def store_publish_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._was_published = Article.objects.get(pk=instance.pk).is_published
        except Article.DoesNotExist:
            instance._was_published = False
    else:
        instance._was_published = False


@receiver(post_save, sender=Article)
def notify_subscribers_on_publish(sender, instance, created, **kwargs):
    if not instance.is_published:
        return

    if created:
        _send_new_article_notification(instance)
    else:
        was_published = getattr(instance, '_was_published', False)
        if instance.is_published and not was_published:
            _send_new_article_notification(instance)


def _send_new_article_notification(article):
    if ArticleNotificationSent.objects.filter(article=article).exists():
        return

    from django.core.mail import send_mail
    from django.conf import settings
    from django.urls import reverse

    confirmed_subscribers = ArticleSubscriber.objects.filter(status='confirmed')

    if not confirmed_subscribers.exists():
        return

    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    article_url = f"{site_url}{article.get_absolute_url()}"

    subject = f"Nouvel article : {article.title}"

    for subscriber in confirmed_subscribers:
        unsubscribe_url = f"{site_url}{reverse('unsubscribe', kwargs={'token': subscriber.unsubscribe_token})}"

        name_greeting = f", {subscriber.name}" if subscriber.name else ""
        message = f"""Bonjour{name_greeting} !

Un nouvel article vient d'être publié sur TechSpace Portfolio.

Titre : {article.title}

{article.excerpt}

Lire l'article : {article_url}

---

Pour vous désabonner de la newsletter, cliquez ici :
{unsubscribe_url}
"""

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=True,
            )
        except Exception:
            pass

    ArticleNotificationSent.objects.create(article=article)
