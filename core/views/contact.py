"""
contact/views.py
"""
import logging

from django.contrib import messages
from django.core.mail import EmailMessage, BadHeaderError
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import ContactForm

logger = logging.getLogger(__name__)


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        # form.save() écrit le ContactMessage en base (grâce au ModelForm).
        # Le champ honeypot "website" n'est pas sur le modèle donc il est
        # simplement ignoré ici -- clean_website() a déjà bloqué les bots
        # avant qu'on arrive à ce point.
        contact_message = form.save()

        email_sent = self._send_notification_email(contact_message)
        contact_message.email_sent = email_sent
        contact_message.save(update_fields=["email_sent"])

        if email_sent:
            messages.success(
                self.request,
                "Merci pour votre message ! Je vous répondrai dans les plus brefs délais."
            )
        else:
            # Le message est bien enregistré en base même si le mail échoue,
            # donc rien n'est perdu -- mais on prévient l'utilisateur au cas où.
            messages.success(
                self.request,
                "Votre message a bien été reçu, merci !"
            )
            logger.error("Échec de l'envoi de l'email de notification pour le message #%s", contact_message.pk)

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Certains champs nécessitent votre attention, merci de vérifier le formulaire."
        )
        return super().form_invalid(form)

    def _send_notification_email(self, contact_message) -> bool:
        """Envoie une notification à l'adresse admin définie dans settings.CONTACT_RECIPIENT_EMAIL."""
        subject = f"[TechSpace] Nouveau message : {contact_message.subject}"
        body = (
            f"Nom : {contact_message.name}\n"
            f"Email : {contact_message.email}\n"
            f"Sujet : {contact_message.subject}\n\n"
            f"Message :\n{contact_message.message}\n"
        )
        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_RECIPIENT_EMAIL],
                reply_to=[contact_message.email],  # tu peux répondre directement au client
            )
            email.send(fail_silently=False)
            return True
        except BadHeaderError:
            logger.error("En-tête invalide détecté dans le message #%s", contact_message.pk)
            return False
        except Exception:
            logger.exception("Erreur lors de l'envoi de l'email pour le message #%s", contact_message.pk)
            return False