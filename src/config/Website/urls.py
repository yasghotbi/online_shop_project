from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter


from .views import (
    CategoryViewSet, ProductViewSet,
    ReviewAPIView, StoreListAPIView, StoreDetailAPIView, ProductSearchAPIView, ActiveDiscountsView
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', TemplateView.as_view(template_name='website/home.html'), name='home-page'),
    path('api/', include(router.urls)),

    path('category/<int:pk>/', TemplateView.as_view(template_name='website/category_page.html'), name='category-page'),
    # path('product/<int:pk>/', TemplateView.as_view(template_name='website/product_page.html'), name='product-page'),
    path('cart/', TemplateView.as_view(template_name='website/cart_page.html'), name='cart-page'),
    path('search/', TemplateView.as_view(template_name='website/search-products.html'), name='search-page'),
    re_path(r'^product/\d+/$', TemplateView.as_view(template_name='website/product_page.html'),
            name="product-detail-page"),
    path('products/<int:product_id>/reviews/', ReviewAPIView.as_view(), name='product-reviews'),

    # API for stores
    path('stores-api/', StoreListAPIView.as_view(), name='store-list'),
    # path('stores/<int:pk>/', StoreDetailAPIView.as_view(), name='store-detail-api'),

    # Store products API
    path('stores/<int:store_id>/products/', ProductViewSet.as_view({'get': 'list'}), name='store-products'),
    path('category/<int:category_id>/products/', ProductViewSet.as_view({'get': 'list'}), name='product-list-category'),
    # path('products_search/', ProductViewSet.as_view({'get': 'list'}), name='products_search'),

    # Web page for store details
    re_path(r'^store-detail/(?P<pk>\d+)/$', TemplateView.as_view(template_name='website/store-detail.html'),
            name='store-detail'),

    re_path('stores/', TemplateView.as_view(template_name='website/store-list.html'), name='store-list-page'),
    path('api/search/', ProductSearchAPIView.as_view(), name='api-search-products'),
    path('active-discounts/', ActiveDiscountsView.as_view(), name='active-discounts'),





]
