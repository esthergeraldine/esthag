"""
contact/models.py

Historique optionnel des messages envoyés depuis le formulaire de contact.
Même si le mail part correctement, garder une trace en base te permet de
retrouver un message si jamais ton SMTP a un souci ou si un mail atterrit
dans les spams.
"""
from django.db import models


class ContactMessage(models.Model):
    name = models.CharField("Nom", max_length=150)
    email = models.EmailField("Email")
    company = models.CharField("Entreprise", max_length=200, blank=True, default="")
    phone = models.CharField("Téléphone", max_length=50, blank=True, default="")
    subject = models.CharField("Sujet", max_length=200)
    message = models.TextField("Message")

    is_read = models.BooleanField("Lu", default=False)
    email_sent = models.BooleanField("Email envoyé", default=False)
    created_at = models.DateTimeField("Reçu le", auto_now_add=True)

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.name} ({self.created_at:%d/%m/%Y})"