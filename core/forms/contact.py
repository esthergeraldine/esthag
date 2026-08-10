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

    company = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "placeholder": "Company name",
        "class": "field w-full rounded-xl px-4 py-3 text-sm text-[#3a2a2c] bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-burgundy/30 focus:border-burgundy placeholder-gray-400",
    }))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "placeholder": "+1 (000) 000-0000",
        "class": "field w-full rounded-xl px-4 py-3 text-sm text-[#3a2a2c] bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-burgundy/30 focus:border-burgundy placeholder-gray-400",
    }))

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Your name",
                "class": "field w-full rounded-xl px-4 py-3 text-sm text-[#3a2a2c] bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-burgundy/30 focus:border-burgundy placeholder-gray-400",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "you@example.com",
                "class": "field w-full rounded-xl px-4 py-3 text-sm text-[#3a2a2c] bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-burgundy/30 focus:border-burgundy placeholder-gray-400",
            }),
            "subject": forms.TextInput(attrs={
                "placeholder": "How can we help?",
                "class": "field w-full rounded-xl px-4 py-3 text-sm text-[#3a2a2c] bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-burgundy/30 focus:border-burgundy placeholder-gray-400",
            }),
            "message": forms.Textarea(attrs={
                "placeholder": "Write your message...",
                "rows": 5,
                "class": "field w-full rounded-xl px-4 py-3 text-sm text-[#3a2a2c] bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-burgundy/30 focus:border-burgundy placeholder-gray-400 resize-none",
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
