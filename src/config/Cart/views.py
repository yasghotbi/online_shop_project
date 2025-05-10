from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from Cart.utils import load_cart_from_cookie, save_cart_to_cookie
from Cart.serializers import CartItemSerializer
from Vendors.models import Product
#-----------------------------------------------------------------------------------------------------------------------
def enrich_cart(cart):
    new_items = []
    total_quantity = 0
    total_price = 0

    for item in cart['items']:
        try:
            product = Product.objects.get(id=item['product'])
            enriched_item = {
                'product': item['product'],
                'quantity': item['quantity'],
                'product_name': product.name,
                'product_price': product.price_after_discount,
                'item_total_price': product.price_after_discount * item['quantity'],
            }
            total_quantity += item['quantity']
            total_price += enriched_item['item_total_price']
            new_items.append(enriched_item)
        except Product.DoesNotExist:
            continue

    return {
        'items': new_items,
        'total_quantity': total_quantity,
        'total_price': total_price,
    }
#-----------------------------------------------------------------------------------------------------------------------
class CartViewSet(viewsets.ViewSet):

    def list(self, request):
        cart = load_cart_from_cookie(request)
        enriched = enrich_cart(cart)
        return Response(enriched)

    def create(self, request):
        cart = load_cart_from_cookie(request)

        item_ser = CartItemSerializer(data=request.data)
        item_ser.is_valid(raise_exception=True)
        valid_item = item_ser.validated_data

        for it in cart['items']:
            if it['product'] == valid_item['product']:
                it['quantity'] += valid_item['quantity']
                break
        else:
            cart['items'].append(valid_item)

        resp_data = enrich_cart(cart)
        resp = Response(resp_data, status=status.HTTP_201_CREATED)
        save_cart_to_cookie(resp, cart)
        return resp

    def partial_update(self, request, pk=None):
        cart = load_cart_from_cookie(request)
        try:
            qty = int(request.data.get('quantity', ''))
            assert qty >= 0
        except (ValueError, AssertionError):
            return Response({'detail': 'مقدار quantity باید عدد صحیح غیرمنفی باشد.'},
                            status=status.HTTP_400_BAD_REQUEST)

        updated = False
        new_items = []
        for it in cart['items']:
            if it['product'] == int(pk):
                if qty > 0:
                    it['quantity'] = qty
                    new_items.append(it)
                updated = True
            else:
                new_items.append(it)

        if not updated:
            return Response({'detail': 'محصول پیدا نشد.'},
                            status=status.HTTP_404_NOT_FOUND)

        cart['items'] = new_items
        resp_data = enrich_cart(cart)
        resp = Response(resp_data, status=status.HTTP_200_OK)
        save_cart_to_cookie(resp, cart)
        return resp

    def destroy(self, request, pk=None):
        cart = load_cart_from_cookie(request)
        cart['items'] = [it for it in cart['items'] if it['product'] != int(pk)]

        resp_data = enrich_cart(cart)
        resp = Response(resp_data, status=status.HTTP_200_OK)
        save_cart_to_cookie(resp, cart)
        return resp

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = {'items': []}
        resp_data = enrich_cart(cart)
        resp = Response(resp_data, status=status.HTTP_200_OK)
        save_cart_to_cookie(resp, cart)
        return resp
#-----------------------------------------------------------------------------------------------------------------------

def cart_view(request):
    return render(request, 'cart/cart.html')

#-----------------------------------------------------------------------------------------------------------------------
