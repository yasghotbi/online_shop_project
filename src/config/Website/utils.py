from django.shortcuts import get_object_or_404
from Customers.models import OrderItem
from Vendors.models import Product

def has_product_in_order(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        return OrderItem.objects.filter(
            order__customer=request.user,
            product=product,
            order__is_paid=True
        ).exists()
    return False