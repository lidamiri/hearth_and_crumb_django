from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product

from .cart import Cart
from .forms import AddToCartForm, CartUpdateForm, CheckoutForm, OrderLookupForm
from .models import Order
from .services import OrderError, place_order


def cart_detail(request):
    return render(request, "orders/cart.html", {"update_form": CartUpdateForm()})


@require_POST
def cart_add(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    form = AddToCartForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Choose a quantity between 1 and 50.")
        return redirect(product.get_absolute_url())
    allowed = Cart(request).add(product, form.cleaned_data["quantity"])
    if allowed == 0:
        messages.error(request, f"{product.name} is sold out right now.")
        return redirect(product.get_absolute_url())
    messages.success(request, f"{product.name} is in your basket.")
    return redirect("orders:cart")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = CartUpdateForm(request.POST)
    if form.is_valid():
        Cart(request).add(product, form.cleaned_data["quantity"], override=True)
        messages.success(request, f"Updated {product.name}.")
    else:
        messages.error(request, "Quantity must be between 0 and 50.")
    return redirect("orders:cart")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Cart(request).remove(product)
    messages.info(request, f"Removed {product.name} from your basket.")
    return redirect("orders:cart")


def checkout(request):
    cart = Cart(request)
    if cart.is_empty:
        messages.info(request, "Your basket is empty.")
        return redirect("orders:cart")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = place_order(cart, form)
            except OrderError as error:
                messages.error(request, str(error))
                return redirect("orders:cart")
            request.session["last_order"] = order.reference
            return redirect("orders:complete")
    else:
        form = CheckoutForm()
    return render(request, "orders/checkout.html", {"form": form})


def order_complete(request):
    reference = request.session.get("last_order")
    if not reference:
        return redirect("orders:track")
    order = get_object_or_404(Order.objects.prefetch_related("items"), reference=reference)
    return render(request, "orders/complete.html", {"order": order})


def track_order(request):
    order = None
    if request.method == "POST":
        form = OrderLookupForm(request.POST)
        if form.is_valid():
            order = (
                Order.objects.prefetch_related("items")
                .filter(reference=form.cleaned_data["reference"], email__iexact=form.cleaned_data["email"])
                .first()
            )
            if order is None:
                messages.error(request, "No order matches that reference and email address.")
    else:
        form = OrderLookupForm()
    return render(request, "orders/track.html", {"form": form, "order": order})
