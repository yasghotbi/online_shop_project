from rest_framework import serializers
from django.shortcuts import get_object_or_404
from Vendors.models import Product
#-----------------------------------------------------------------------------------------------------------------------
class CartItemSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product(self, value):
        get_object_or_404(Product, pk=value)
        return value
#-----------------------------------------------------------------------------------------------------------------------

class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

#-----------------------------------------------------------------------------------------------------------------------
