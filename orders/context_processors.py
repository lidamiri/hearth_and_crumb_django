from .cart import Cart


def basket(request):
    return {"basket": Cart(request)}
