from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class CatalogTests(TestCase):
    def setUp(self):
        self.breads = Category.objects.create(name="Breads", sort_order=1)
        self.cakes = Category.objects.create(name="Cakes", sort_order=2)
        self.loaf = Product.objects.create(
            category=self.breads,
            name="Country Sourdough",
            summary="Open crumb loaf",
            description="A slow fermented loaf.",
            price=Decimal("6.50"),
            stock=5,
            is_featured=True,
        )
        self.torte = Product.objects.create(
            category=self.cakes,
            name="Chocolate Torte",
            summary="Rich flourless torte",
            description="Dark chocolate and cream.",
            price=Decimal("29.50"),
            stock=2,
        )

    def test_slug_is_generated_from_name(self):
        self.assertEqual(self.loaf.slug, "country-sourdough")

    def test_duplicate_names_get_unique_slugs(self):
        clone = Product.objects.create(
            category=self.breads,
            name="Country Sourdough",
            summary="Copy",
            description="Copy",
            price=Decimal("1.00"),
        )
        self.assertNotEqual(clone.slug, self.loaf.slug)
        self.assertTrue(clone.slug.startswith("country-sourdough"))

    def test_home_lists_featured_products(self):
        response = self.client.get(reverse("catalog:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Country Sourdough")
        self.assertNotContains(response, "Chocolate Torte")

    def test_search_filters_products(self):
        response = self.client.get(reverse("catalog:product_list"), {"q": "torte"})
        self.assertContains(response, "Chocolate Torte")
        self.assertNotContains(response, "Country Sourdough")

    def test_category_page_filters_by_category(self):
        response = self.client.get(reverse("catalog:category", args=[self.cakes.slug]))
        self.assertContains(response, "Chocolate Torte")
        self.assertNotContains(response, "Country Sourdough")

    def test_unavailable_product_is_hidden(self):
        self.torte.is_available = False
        self.torte.save()
        response = self.client.get(reverse("catalog:product", args=[self.torte.slug]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("catalog:product_list"))
        self.assertNotContains(response, "Chocolate Torte")

    def test_missing_product_returns_404(self):
        response = self.client.get(reverse("catalog:product", args=["does-not-exist"]))
        self.assertEqual(response.status_code, 404)
