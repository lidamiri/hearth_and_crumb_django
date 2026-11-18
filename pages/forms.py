from django import forms
from django.core.exceptions import ValidationError

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, label="Leave this field empty")

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise ValidationError("Spam detected.")
        return ""
