from django.urls import path
from django.views.generic import TemplateView

from .views import EmployeeRecordView, RegisterEmployeeView, StoreView, StoreProfile, vendor_dashboard, StoreUpdateView, \
    EmployeeListView, EmployeeUpdateView, EmployeeDetailView, employee_register, StoreOrdersView, StoreOrderDetailView, \
    StoreOrderStatusUpdateView, ProfileUpdateView, ProfileView, DashboardSummaryAPIView
from .views import ProductListView,ProductDetailView,ProductCreateView,ProductUpdateView,DiscountListView,DiscountCreateView,DiscountDetailView,DiscountUpdateView
urlpatterns = [
    path('dashboard/', vendor_dashboard, name='vendor-dashboard'),
    path('employee_register/', employee_register, name='employee_register'),
    path('register-employee/', RegisterEmployeeView.as_view(), name='register-employee'),
    path('record-employee/', EmployeeRecordView.as_view(), name='employee-record'),
    # path('register-owner/', RegisterOwnerView.as_view(), name='register-owner'),
    path('record-store/', StoreView.as_view(), name='record-store'),
    path('store/profile/<int:pk>/', StoreProfile.as_view(), name='store-profile'),
    path('store/<int:pk>/edit/', StoreUpdateView.as_view(), name='store-update'),
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employee/<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee-update'),
    path('employee/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('products/', ProductListView.as_view(), name='product-list-vendor'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail-vendor'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product-update'),
    path('discounts/', DiscountListView.as_view(), name='discount-list'),
    path('discounts/create/', DiscountCreateView.as_view(), name='discount-create'),
    path('discounts/<int:pk>/', DiscountDetailView.as_view(), name='discount-detail'),
    path('discounts/<int:pk>/edit/', DiscountUpdateView.as_view(), name='discount-update'),
    path('orders/', StoreOrdersView.as_view(), name='store-orders'),
    path('order/<int:pk>/', StoreOrderDetailView.as_view(), name='store-orders-detail'),
    path('order/<int:pk>/edit/', StoreOrderStatusUpdateView.as_view(), name='store-orders-update'),
    path('profile/<int:pk>/edit/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
 path('dashboard-summary/', DashboardSummaryAPIView.as_view(), name='dashboard-summary'),
 path('summary/', TemplateView.as_view(template_name="vendors/summery.html"), name='summary'),




    ]

