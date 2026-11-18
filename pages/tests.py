from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


class ContactTests(TestCase):
    def test_contact_form_stores_message(self):
        response = self.client.post(
            reverse("pages:contact"),
            {
                "name": "Sam",
                "email": "sam@example.com",
                "subject": "Wedding cake",
                "message": "Can we order a three tier cake for June?",
                "website": "",
            },
        )
        self.assertRedirects(response, reverse("pages:contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_honeypot_blocks_bots(self):
        self.client.post(
            reverse("pages:contact"),
            {
                "name": "Bot",
                "email": "bot@example.com",
                "subject": "Spam",
                "message": "Buy now",
                "website": "http://spam.example",
            },
        )
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_about_page_renders(self):
        response = self.client.get(reverse("pages:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hearth and Crumb")
