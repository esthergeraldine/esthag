"""
contact/forms.py
"""
from django import forms

from ..models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot : champ invisible pour l'utilisateur humain (caché en CSS côté template).
    # Un bot qui remplit les champs automatiquement va aussi remplir celui-ci ->
    # on le détecte comme spam dans clean_website().
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Votre nom",
                "class": "field w-full rounded-lg px-5 py-4 text-[14px] text-boss-text bg-warm-white border border-rose-pale focus:outline-none focus:ring-2 focus:ring-burgundy/30",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Votre email",
                "class": "field w-full rounded-lg px-5 py-4 text-[14px] text-boss-text bg-warm-white border border-rose-pale focus:outline-none focus:ring-2 focus:ring-burgundy/30",
            }),
            "subject": forms.TextInput(attrs={
                "placeholder": "Sujet",
                "class": "field w-full rounded-lg px-5 py-4 text-[14px] text-boss-text bg-warm-white border border-rose-pale focus:outline-none focus:ring-2 focus:ring-burgundy/30",
            }),
            "message": forms.Textarea(attrs={
                "placeholder": "Votre message",
                "rows": 6,
                "class": "field w-full rounded-lg px-5 py-4 text-[14px] text-boss-text bg-warm-white border border-rose-pale focus:outline-none focus:ring-2 focus:ring-burgundy/30 resize-y",
            }),
        }
        labels = {
            "name": "",
            "email": "",
            "subject": "",
            "message": "",
        }

    def clean_website(self):
        """Si ce champ caché est rempli, c'est un bot -> on rejette silencieusement."""
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Spam détecté.")
        return value

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 10:
            raise forms.ValidationError("Votre message est un peu court, dites m'en un peu plus !")
        return message