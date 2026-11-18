from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import Category, Product


def home(request):
    featured = Product.objects.select_related("category").filter(is_available=True, is_featured=True)[:6]
    categories = Category.objects.all()
    return render(request, "catalog/home.html", {"featured": featured, "categories": categories})


def product_list(request, category=None):
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category").filter(is_available=True)
    if category is not None:
        products = products.filter(category=category)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(summary__icontains=query) | Q(description__icontains=query)
        )
    return render(
        request,
        "catalog/product_list.html",
        {
            "products": products,
            "categories": Category.objects.all(),
            "active_category": category,
            "query": query,
        },
    )


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return product_list(request, category=category)


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_available=True)
    related = Product.objects.filter(category=product.category, is_available=True).exclude(pk=product.pk)[:3]
    return render(request, "catalog/product_detail.html", {"product": product, "related": related})


def not_found(request, exception=None):
    return render(request, "404.html", status=404)
