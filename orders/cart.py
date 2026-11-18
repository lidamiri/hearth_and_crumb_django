from decimal import Decimal

from django.conf import settings

from catalog.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.data = self.session.get(settings.CART_SESSION_KEY, {})

    def _persist(self):
        self.session[settings.CART_SESSION_KEY] = self.data
        self.session.modified = True

    def add(self, product, quantity=1, override=False):
        key = str(product.pk)
        current = self.data.get(key, {}).get("quantity", 0)
        requested = quantity if override else current + quantity
        allowed = min(requested, product.stock, settings.MAX_LINE_QUANTITY)
        if allowed <= 0 or not product.is_available:
            self.data.pop(key, None)
        else:
            self.data[key] = {"quantity": allowed}
        self._persist()
        return allowed

    def remove(self, product):
        self.data.pop(str(product.pk), None)
        self._persist()

    def clear(self):
        self.data = {}
        self.session.pop(settings.CART_SESSION_KEY, None)
        self.session.modified = True

    def lines(self):
        products = Product.objects.in_bulk([int(key) for key in self.data])
        result = []
        for key, item in self.data.items():
            product = products.get(int(key))
            if product is None:
                continue
            quantity = min(item["quantity"], product.stock)
            if quantity <= 0:
                continue
            result.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "line_total": product.price * quantity,
                }
            )
        return result

    def __iter__(self):
        return iter(self.lines())

    def __len__(self):
        return sum(item["quantity"] for item in self.data.values())

    @property
    def total(self):
        return sum((line["line_total"] for line in self.lines()), Decimal("0.00"))

    @property
    def is_empty(self):
        return len(self) == 0
