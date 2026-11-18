from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Order

DATETIME_INPUT_FORMATS = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"]


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=50, initial=1)


class CartUpdateForm(forms.Form):
    quantity = forms.IntegerField(min_value=0, max_value=50)


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "email", "phone", "pickup_slot", "notes"]
        labels = {
            "customer_name": "Full name",
            "pickup_slot": "Pickup time",
        }
        widgets = {
            "pickup_slot": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pickup_slot"].input_formats = DATETIME_INPUT_FORMATS

    def clean_pickup_slot(self):
        slot = self.cleaned_data["pickup_slot"]
        if slot <= timezone.now():
            raise ValidationError("Choose a pickup time in the future.")
        return slot


class OrderLookupForm(forms.Form):
    reference = forms.CharField(max_length=12)
    email = forms.EmailField()

    def clean_reference(self):
        return self.cleaned_data["reference"].strip().upper()
