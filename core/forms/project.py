from django import forms
from ..models import ProjectIdea


class ProjectIdeaForm(forms.ModelForm):
    class Meta:
        model = ProjectIdea
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Votre nom",
                "class": "w-full rounded-lg px-4 py-3 text-[14px] bg-warm-white border border-rose-pale focus:outline-none focus:ring-2 focus:ring-burgundy/30",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Votre email",
                "class": "w-full rounded-lg px-4 py-3 text-[14px] bg-warm-white border border-rose-pale focus:outline-none focus:ring-2 focus:ring-burgundy/30",
            }),
            "message": forms.Textarea(attrs={
                "placeholder": "Décrivez votre idée...",
                "rows": 4,
                "class": "w-full rounded-lg px-4 py-3 text-[14px] bg-warm-white border border-rose-pale focus:outline-none focus:ring-2 focus:ring-burgundy/30 resize-y",
            }),
        }
        labels = {
            "name": "",
            "email": "",
            "message": "",
        }
