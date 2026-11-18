from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, Product

CATEGORIES = [
    ("Breads", "Naturally leavened loaves and rolls baked every morning.", 1),
    ("Pastries", "Laminated viennoiserie with a long, cold fermentation.", 2),
    ("Cakes", "Whole cakes and slices for celebrations and afternoon tea.", 3),
    ("Cookies", "Chewy, crisp and sold by the half dozen.", 4),
    ("Seasonal", "Limited bakes that follow the harvest calendar.", 5),
]

PRODUCTS = [
    ("Country Sourdough", "Breads", "Open crumb, blistered crust, 36 hour ferment.", "A rustic loaf made with stone milled wheat and a 36 hour cold ferment.", "6.50", 24, True, "gluten, sesame"),
    ("Seeded Rye", "Breads", "Dense rye with sunflower and flax seeds.", "A dense, aromatic rye with toasted sunflower and flax seeds, ideal for open sandwiches.", "7.25", 14, False, "gluten, seeds"),
    ("Brioche Buns", "Breads", "Six buns enriched with butter and egg.", "Soft enriched buns, six to a bag, ready for burgers or sliders.", "5.80", 30, False, "gluten, egg, dairy"),
    ("Almond Croissant", "Pastries", "Twice baked with frangipane and flaked almonds.", "Butter croissant filled with house almond frangipane and toasted flakes.", "4.20", 18, True, "gluten, egg, dairy, nuts"),
    ("Pain au Chocolat", "Pastries", "Two bars of dark chocolate in laminated dough.", "Classic laminated dough with two bars of 70 percent dark chocolate.", "3.60", 26, False, "gluten, egg, dairy"),
    ("Cardamom Knot", "Pastries", "Swedish style knot with pearl sugar.", "A soft knot scented with cardamom and finished with pearl sugar.", "3.40", 12, False, "gluten, egg, dairy"),
    ("Lemon Drizzle Cake", "Cakes", "Olive oil sponge soaked in lemon syrup.", "Moist sponge made with olive oil, soaked in lemon syrup and finished with zest.", "24.00", 6, True, "gluten, egg, dairy"),
    ("Dark Chocolate Torte", "Cakes", "Flourless torte with sea salt cream.", "A flourless torte of dark chocolate finished with whipped sea salt cream.", "29.50", 4, False, "egg, dairy"),
    ("Honey Oat Cake", "Cakes", "Slice of oat cake with wildflower honey.", "A single generous slice of oat cake with wildflower honey and toasted oats.", "4.75", 10, False, "gluten, oats, egg"),
    ("Brown Butter Cookie", "Cookies", "Crisp edges and a soft centre.", "Brown butter dough with a crisp edge and a soft, chewy centre.", "2.40", 40, False, "gluten, egg, dairy"),
    ("Oatmeal Raisin Cookie", "Cookies", "Chewy oats with plump raisins.", "Oats, cinnamon and plump raisins in a chewy cookie.", "2.20", 36, False, "gluten, oats, egg"),
    ("Pumpkin Spice Loaf", "Seasonal", "Autumn loaf with clove and nutmeg.", "A moist loaf of pumpkin, clove and nutmeg, available in autumn only.", "6.90", 8, True, "gluten, egg, dairy"),
    ("Strawberry Galette", "Seasonal", "Summer galette with vanilla custard.", "A rustic galette of strawberries and vanilla custard in a buttery crust.", "12.50", 5, False, "gluten, egg, dairy"),
]


class Command(BaseCommand):
    help = "Load the demo categories and products used on the storefront."

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for name, description, order in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                name=name,
                defaults={"description": description, "sort_order": order},
            )
            categories[name] = category
        created = 0
        for name, category_name, summary, description, price, stock, featured, allergens in PRODUCTS:
            _, was_created = Product.objects.update_or_create(
                name=name,
                defaults={
                    "category": categories[category_name],
                    "summary": summary,
                    "description": description,
                    "price": Decimal(price),
                    "stock": stock,
                    "is_featured": featured,
                    "is_available": True,
                    "allergens": allergens,
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(CATEGORIES)} categories and {len(PRODUCTS)} products ({created} new)."))
