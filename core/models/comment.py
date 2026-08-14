from django.db import models
from django.utils import timezone


class Comment(models.Model):
    STATUS_CHOICES = (
        ('published', 'Publié'),
        ('hidden', 'Masqué'),
        ('spam', 'Spam'),
    )

    article = models.ForeignKey(
        'Article',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    subscriber = models.ForeignKey(
        'ArticleSubscriber',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name="Abonné"
    )
    name = models.CharField("Nom", max_length=100, blank=True)
    email = models.EmailField("Email", blank=True)
    content = models.TextField("Contenu")

    status = models.CharField(
        "Statut",
        max_length=20,
        choices=STATUS_CHOICES,
        default='published'
    )
    likes_count = models.PositiveIntegerField("Likes", default=0)
    replies_count = models.PositiveIntegerField("Réponses", default=0)

    created_date = models.DateTimeField("Date de création", auto_now_add=True)
    updated_date = models.DateTimeField("Dernière modification", auto_now=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=['article', 'status', '-created_date']),
            models.Index(fields=['parent']),
            models.Index(fields=['subscriber']),
        ]

    def __str__(self):
        display_name = self.display_name
        return f"{display_name} — {self.article.title[:30]}"

    @property
    def display_name(self):
        if self.subscriber and self.subscriber.name:
            return self.subscriber.name
        return self.name or "Anonyme"

    @property
    def is_reply(self):
        return self.parent is not None

    def get_article_author_email(self):
        if self.article and self.article.author and self.article.author.email:
            return self.article.author.email
        return None

    def is_article_author(self):
        if self.subscriber and self.article and self.article.author:
            return self.subscriber.email.lower() == self.article.author.email.lower()
        article_author_email = self.get_article_author_email()
        if article_author_email and self.email:
            return self.email.lower() == article_author_email.lower()
        return False


class CommentLike(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("comment", "session_key")
        verbose_name = "Like de commentaire"
        verbose_name_plural = "Likes de commentaires"

    def __str__(self):
        return f"Like — {self.comment.name}"


class ReportedComment(models.Model):
    REASON_CHOICES = (
        ('spam', 'Spam'),
        ('inappropriate', 'Contenu inapproprié'),
        ('harassment', 'Harcèlement'),
        ('other', 'Autre'),
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reason = models.CharField(
        "Motif",
        max_length=20,
        choices=REASON_CHOICES
    )
    session_key = models.CharField("Session", max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commentaire signalé"
        verbose_name_plural = "Commentaires signalés"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Signalement — {self.comment.name} ({self.get_reason_display()})"
