from rest_framework.routers import DefaultRouter
from Cart.views import CartViewSet
from django.urls import path
from .views import cart_view
router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = router.urls




