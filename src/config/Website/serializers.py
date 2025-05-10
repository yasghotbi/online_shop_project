from rest_framework import serializers
from rest_framework.reverse import reverse
from Vendors.models import Category, Product, Discount, Store
from Website.models import Rating, Comment


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children', 'products', 'created_at', 'updated_at']

    def get_children(self, obj):
        depth = self.context.get('depth', 1)
        if depth <= 0:
            return []
        qs = obj.children.filter(is_deleted=False)

        serializer = CategoryMiniSerializer(qs, many=True, context=self.context)
        return serializer.data

    def get_products(self, obj):
        qs = obj.products.filter(is_deleted=False)
        return ProductSerializer(qs, many=True, context=self.context).data


class CategoryMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']

class ProductSerializer(serializers.ModelSerializer):
    category = CategoryMiniSerializer(read_only=True)
    price_after_discount = serializers.SerializerMethodField()
    discount_name = serializers.SerializerMethodField()
    discount_value = serializers.SerializerMethodField()
    discount_type = serializers.SerializerMethodField()
    description = serializers.CharField(read_only=True)
    variant = serializers.JSONField()
    store_name = serializers.CharField(source='store.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'store', 'category',
            'discount', 'price', 'price_after_discount',
            'discount_name', 'discount_value', 'discount_type',
            'created_at', 'updated_at', 'is_deleted', 'image', 'variant','stock','store_name','category_name','avg_rating'
        ]

    def get_price_after_discount(self, obj):
        return obj.price_after_discount

    def get_discount_name(self, obj):
        return obj.discount.name if obj.discount else None

    def get_discount_value(self, obj):
        return float(obj.discount.value) if obj.discount else None

    def get_discount_type(self, obj):
        return obj.discount.type if obj.discount else None
class RatingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    rating = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Rating
        fields = ['user', 'product', 'rating', 'review']
        read_only_fields = ('product', 'user')

    def get_user(self, obj):
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.username

    def validate_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError('The rating must be between 1 and 5.')
        return value



class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'owner', 'image']

class StoreDetailSerializer(serializers.ModelSerializer):
    products = ProductSerializer(source='product_set', many=True, read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'owner', 'image', 'products']




class DiscountSerializer(serializers.ModelSerializer):
    store_id = serializers.IntegerField(source='store.id')
    store_name = serializers.CharField(source='store.name')
    store_url = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Discount
        fields = ['id', 'name', 'image', 'store_id', 'store_name', 'store_url']

    def get_store_url(self, obj):
        return reverse('store-detail', kwargs={'pk': obj.store.id}, request=self.context.get('request'))

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

class CommentSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'title', 'content', 'created_at', 'created_by_username', 'product']
        read_only_fields = ['id', 'created_at', 'created_by_username']