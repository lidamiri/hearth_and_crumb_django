from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def unique_slug(instance, value, max_length):
    base = slugify(value)[:max_length] or "item"
    candidate = base
    counter = 2
    model = instance.__class__
    while model.objects.exclude(pk=instance.pk).filter(slug=candidate).exists():
        suffix = f"-{counter}"
        candidate = f"{base[: max_length - len(suffix)]}{suffix}"
        counter += 1
    return candidate


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name, 90)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category", kwargs={"slug": self.slug})


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    summary = models.CharField(max_length=240)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    allergens = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category__sort_order", "name"]
        indexes = [models.Index(fields=["is_available", "is_featured"])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name, 140)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product", kwargs={"slug": self.slug})

    @property
    def in_stock(self):
        return self.is_available and self.stock > 0
