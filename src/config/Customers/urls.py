from django.urls import path
from .views import CustomerDetailView, CustomerUpdateView, AddressListView, AddressDetailView, AddressUpdateView, \
    OrderViewSet, CheckoutPageView, UserAddressesForCheckoutAPIView, customer_dashboard, AddressCreateView, \
    OrderListView, OrderDetailView,UserRatingsListView
checkout_view = OrderViewSet.as_view({'post': 'checkout'})
urlpatterns = [

    path('profile/<int:pk>/', CustomerDetailView.as_view(), name='customer-profile'),
    path('profile/<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer-profile-edit'),
    path('addresses/', AddressListView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('addresses/<int:pk>/edit/', AddressUpdateView.as_view(), name='address-update'),
    path('addresses/create/', AddressCreateView.as_view(), name='address-create'),
    path('order/', CheckoutPageView.as_view(), name='address-update'),
    path('checkout/addresses/', UserAddressesForCheckoutAPIView.as_view(), name='checkout-addresses'),
    path('dashboard/', customer_dashboard, name='dashboard-customer'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('my-ratings/', UserRatingsListView.as_view(), name='user_ratings_list'),
    path('checkout/', checkout_view, name='api-checkout'),
]
