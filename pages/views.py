from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ContactForm


def about(request):
    return render(request, "pages/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you. We received your message and will reply within two working days.")
            return redirect(reverse("pages:contact"))
    else:
        form = ContactForm()
    return render(request, "pages/contact.html", {"form": form})
