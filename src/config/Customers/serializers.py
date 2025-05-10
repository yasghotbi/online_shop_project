from rest_framework import serializers
from Cart.utils import load_cart_from_cookie
from Vendors.models import Product
from .models import Address, Order, OrderItem
from rest_framework import serializers
from .models import Order, OrderItem, Address, Product

class OrderCreateSerializer(serializers.ModelSerializer):
    address_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'address_id', 'total_price']
        read_only_fields = ['id', 'total_price']

    def validate_address_id(self, value):
        user = self.context['request'].user
        address = Address.objects.filter(id=value, customer=user).first()
        if not address:
            raise serializers.ValidationError('آدرس معتبر نیست.')
        return value

    def create(self, validated_data):
        request = self.context['request']
        cart = load_cart_from_cookie(request)

        if not cart['items']:
            raise serializers.ValidationError('سبد خرید شما خالی است.')

        user = request.user
        address = Address.objects.get(id=validated_data['address_id'])

        total_price = 0
        order = Order.objects.create(
            customer=user,
            address=address,
            status='pending',
            total_price=0
        )

        for item in cart['items']:
            product = Product.objects.get(id=item['product'])
            quantity = item['quantity']
            price = product.price_after_discount

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )

            total_price += price * quantity

        order.total_price = total_price
        order.save()

        return order

#v
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'title', 'address_text', 'post_code', 'city', 'created_at', 'updated_at', 'is_deleted']