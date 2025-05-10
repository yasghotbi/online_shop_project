from django.db.models import Case, When, F, Value, FloatField, Sum, Avg, Prefetch,Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from rest_framework.generics import ListAPIView
from rest_framework import viewsets, filters, status, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from Vendors.models import Product, Category, Store, Discount
from .models import Rating, Comment
from .serializers import (
    ProductSerializer, CategorySerializer,
    RatingSerializer, StoreSerializer,
    StoreDetailSerializer, DiscountSerializer, CommentSerializer
)
from .utils import has_product_in_order

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

#-----------------------------------------------------------------------------------------------------------------------
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {'parent': ['exact', 'isnull']}
    ordering_fields = ['id', 'name']
    ordering = ['id']

    def get_queryset(self):
        depth = int(self.request.query_params.get('depth', 1))
        queryset = Category.objects.filter(is_deleted=False)
        if depth > 1:
            queryset = queryset.prefetch_related(
                'children',
                Prefetch('products', queryset=Product.objects.filter(is_deleted=False))
            )
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        request = self.request

        depth = int(request.query_params.get('depth', 1))
        context['depth'] = depth
        return context
#-----------------------------------------------------------------------------------------------------------------------

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = ProductSerializer
    pagination_class   = StandardResultsSetPagination
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields   = ['category']
    search_fields      = ['name']
    ordering_fields    = ['id', 'price', 'discount_pct', '-total_sales', 'avg_rating']
    ordering           = ['id']

    def get_queryset(self):
        store_id    = self.kwargs.get('store_id')
        category_id = self.kwargs.get('category_id')

        qs = (
            Product.objects
            .filter(is_deleted=False)
            .select_related('discount', 'category')
            .annotate(
                discount_pct=Case(
                    When(
                        discount__is_deleted=False,
                        discount__type='percentage',
                        discount__start_at__lte=timezone.now(),
                        discount__finished_at__gte=timezone.now(),
                        then=F('discount__value'),
                    ),
                    default=Value(0),
                    output_field=FloatField()
                ),
                total_sales=Sum('orderitems__quantity'),
                avg_rating=Avg(
                    'ratings__rating',
                    filter=Q(ratings__is_deleted=False, ratings__rating__isnull=False)
                ),
            )
        )

        if store_id:
            qs = qs.filter(store_id=store_id)
        if category_id:
            qs = qs.filter(category_id=category_id)

        return qs

#-----------------------------------------------------------------------------------------------------------------------

class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        reviews = product.ratings.filter(is_deleted=False)
        serializer = RatingSerializer(reviews, many=True)

        has_rated = False
        can_rate = False

        if request.user.is_authenticated:
            has_rated = Rating.objects.filter(
                product=product,
                user=request.user,
                rating__isnull=False
            ).exists()
            can_rate = has_product_in_order(request, product_id) and not has_rated


        average_rating = reviews.aggregate(avg=Avg('rating'))['avg']

        return Response({
            'reviews': serializer.data,
            'has_rated': has_rated,
            'can_rate': can_rate,
            'average_rating': average_rating,
        })

    def post(self, request, product_id):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'وارد حساب خود شوید.'}, status=status.HTTP_401_UNAUTHORIZED)

        product = get_object_or_404(Product, id=product_id)

        if 'rating' in request.data:
            if not has_product_in_order(request, product_id):
                return Response(
                    {"detail": "برای ثبت امتیاز باید این محصول را خریده باشید."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Rating.objects.filter(product=product, user=user, rating__isnull=False).exists():
                return Response({'detail': 'شما قبلاً امتیاز داده‌اید.'}, status=status.HTTP_400_BAD_REQUEST)


        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=user)
            return Response({'detail': 'نظر شما با موفقیت ثبت شد.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#-----------------------------------------------------------------------------------------------------------------------

class StoreListAPIView(generics.ListAPIView):
    serializer_class = StoreSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'address']
    ordering_fields = ['created_at', 'rating', 'total_sales']
    ordering = ['-created_at']

    def get_queryset(self):
        return Store.objects.filter(is_deleted=False).annotate(
            rating=Coalesce(Avg('products__ratings__rating'), 0.0),
            total_sales=Coalesce(Sum('products__orderitems__quantity'), 0)
        )
#-----------------------------------------------------------------------------------------------------------------------

class StoreDetailAPIView(generics.RetrieveAPIView):
    queryset = Store.objects.filter(is_deleted=False)
    serializer_class = StoreDetailSerializer
#-----------------------------------------------------------------------------------------------------------------------

class ProductSearchAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        q = self.request.GET.get("search", "")
        return Product.objects.filter(name__icontains=q, is_deleted=False)

#-----------------------------------------------------------------------------------------------------------------------

class ActiveDiscountsView(ListAPIView):
    serializer_class = DiscountSerializer

    def get_queryset(self):
        now = timezone.now()
        return Discount.objects.filter(
            is_deleted=False,
            image__isnull=False,
            start_at__lte=now,
            finished_at__gte=now
        )[:3]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

#-----------------------------------------------------------------------------------------------------------------------


