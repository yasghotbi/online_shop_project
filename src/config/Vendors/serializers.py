from rest_framework import serializers
from .models import Employee, Store

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'user', 'store', 'position', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['user', 'store', 'created_at', 'updated_at']


class StoreSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField()
    total_sales = serializers.IntegerField()

    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'image', 'created_at', 'rating', 'total_sales']



class StoreSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'owner', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['created_at', 'updated_at']