from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.models import Category, Product

from .models import Order


class BasketTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Breads")
        self.loaf = Product.objects.create(
            category=category,
            name="Sourdough",
            summary="Loaf",
            description="Loaf",
            price=Decimal("6.50"),
            stock=3,
        )

    def test_add_is_capped_at_stock(self):
        self.client.post(reverse("orders:cart_add", args=[self.loaf.slug]), {"quantity": 10})
        self.assertEqual(self.client.session["cart"][str(self.loaf.pk)]["quantity"], 3)

    def test_basket_page_shows_total(self):
        self.client.post(reverse("orders:cart_add", args=[self.loaf.slug]), {"quantity": 2})
        response = self.client.get(reverse("orders:cart"))
        self.assertContains(response, "13.00")

    def test_update_to_zero_removes_line(self):
        self.client.post(reverse("orders:cart_add", args=[self.loaf.slug]), {"quantity": 2})
        self.client.post(reverse("orders:cart_update", args=[self.loaf.pk]), {"quantity": 0})
        self.assertNotIn(str(self.loaf.pk), self.client.session.get("cart", {}))

    def test_remove_deletes_line(self):
        self.client.post(reverse("orders:cart_add", args=[self.loaf.slug]), {"quantity": 1})
        self.client.post(reverse("orders:cart_remove", args=[self.loaf.pk]))
        self.assertEqual(self.client.session.get("cart", {}), {})


class CheckoutTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Breads")
        self.loaf = Product.objects.create(
            category=category,
            name="Sourdough",
            summary="Loaf",
            description="Loaf",
            price=Decimal("6.50"),
            stock=3,
        )
        self.client.post(reverse("orders:cart_add", args=[self.loaf.slug]), {"quantity": 2})
        self.pickup = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

    def payload(self, **overrides):
        data = {
            "customer_name": "Ana Lopez",
            "email": "ana@example.com",
            "phone": "",
            "pickup_slot": self.pickup,
            "notes": "",
        }
        data.update(overrides)
        return data

    def test_checkout_creates_order_and_reserves_stock(self):
        response = self.client.post(reverse("orders:checkout"), self.payload())
        self.assertRedirects(response, reverse("orders:complete"))
        order = Order.objects.get()
        self.assertEqual(order.total, Decimal("13.00"))
        self.assertEqual(order.items.get().quantity, 2)
        self.loaf.refresh_from_db()
        self.assertEqual(self.loaf.stock, 1)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_past_pickup_is_rejected(self):
        past = (timezone.now() - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M")
        self.client.post(reverse("orders:checkout"), self.payload(pickup_slot=past))
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_fails_when_stock_dropped(self):
        self.loaf.stock = 1
        self.loaf.save()
        response = self.client.post(reverse("orders:checkout"), self.payload())
        self.assertRedirects(response, reverse("orders:cart"))
        self.assertEqual(Order.objects.count(), 0)

    def test_order_can_be_tracked_by_reference_and_email(self):
        self.client.post(reverse("orders:checkout"), self.payload())
        order = Order.objects.get()
        response = self.client.post(
            reverse("orders:track"),
            {"reference": order.reference.lower(), "email": "ANA@example.com"},
        )
        self.assertContains(response, order.reference)
        self.assertContains(response, "Pending")
