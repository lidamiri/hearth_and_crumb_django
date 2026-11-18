from decimal import Decimal

from django.db import transaction

from catalog.models import Product

from .models import OrderItem


class OrderError(Exception):
    pass


@transaction.atomic
def place_order(cart, form):
    lines = cart.lines()
    if not lines:
        raise OrderError("Your basket is empty.")
    locked = {
        product.pk: product
        for product in Product.objects.select_for_update().filter(pk__in=[line["product"].pk for line in lines])
    }
    requested = {}
    for line in lines:
        pk = line["product"].pk
        quantity = cart.data[str(pk)]["quantity"]
        product = locked.get(pk)
        if product is None or not product.is_available or product.stock < quantity:
            raise OrderError(f"Not enough stock for {line['product'].name}. Please update your basket.")
        requested[pk] = quantity
    order = form.save(commit=False)
    order.total = sum(
        (locked[pk].price * quantity for pk, quantity in requested.items()),
        Decimal("0.00"),
    )
    order.save()
    for pk, quantity in requested.items():
        product = locked[pk]
        product.stock -= quantity
        product.save(update_fields=["stock", "updated_at"])
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            unit_price=product.price,
            quantity=quantity,
        )
    cart.clear()
    return order
