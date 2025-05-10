from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction
from Customers.models import Order, OrderItem
from Vendors.models import Product
from Cart.utils import save_cart_to_cookie, load_cart_from_cookie, clear_cart_cookie
from Website.models import Rating
from .models import CustomUser, Address
from .permissions import IsOwnerObj
from .serializers import AddressSerializer, OrderCreateSerializer
from django.views.generic import TemplateView
                                    #Template-view-customer-panel
#-----------------------------------------------------------------------------------------------------------------------
def customer_dashboard(request):
    return render(request, 'customers/customer-dashboard.html')
class CheckoutPageView(LoginRequiredMixin,TemplateView):
    template_name = 'customers/checkout.html'
#-----------------------------------------------------------------------------------------------------------------------
#profile-customer
class CustomerDetailView(LoginRequiredMixin,DetailView):
    model = CustomUser
    template_name = 'customers/profile_detail.html'
    context_object_name = 'customer'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user != obj:
            raise PermissionDenied("شما فقط به پروفایل خودتان دسترسی دارید.")
        return obj
#-----------------------------------------------------------------------------------------------------------------------
#profile-update
class CustomerUpdateView(LoginRequiredMixin,UpdateView):
    model = CustomUser
    template_name = 'customers/profile_update.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number']
    context_object_name = 'customer'

    def get_success_url(self):
        return reverse_lazy('customer-profile', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user != obj:
            raise PermissionDenied("شما فقط می‌توانید پروفایل خود را ویرایش کنید.")
        return obj

#-----------------------------------------------------------------------------------------------------------------------
#Addresses-list

class AddressListView(LoginRequiredMixin,ListView):
    model = Address
    template_name = 'customers/address_list.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return Address.objects.filter(is_deleted=False, customer=self.request.user)
#-----------------------------------------------------------------------------------------------------------------------
#address-detail
class AddressDetailView(LoginRequiredMixin,DetailView):
    model = Address
    template_name = 'customers/address_detail.html'
    context_object_name = 'address'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.customer != self.request.user:
            raise PermissionDenied("شما فقط به آدرس‌های خود دسترسی دارید.")
        return obj
#-----------------------------------------------------------------------------------------------------------------------
#address-edit
class AddressUpdateView(LoginRequiredMixin,UpdateView):
    model = Address
    template_name = 'customers/address_update.html'
    fields = ['title', 'address_text', 'post_code', 'city','is_deleted']
    context_object_name = 'address'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.customer != self.request.user:
            raise PermissionDenied("شما فقط می‌توانید آدرس‌های خود را ویرایش کنید.")
        return obj

    def get_success_url(self):
        return reverse_lazy('address-list')
#-----------------------------------------------------------------------------------------------------------------------
#create-address
class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    template_name = 'customers/address_create.html'
    fields = ['title', 'address_text', 'post_code', 'city']
    context_object_name = 'address'

    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('address-list')
#-----------------------------------------------------------------------------------------------------------------------
                                        #api-view-order
#-----------------------------------------------------------------------------------------------------------------------
#create-order
class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated,IsOwnerObj]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def checkout(self, request):
        response = Response()
        serializer = OrderCreateSerializer(data=request.data, context={'request': request, 'response': response})

        if serializer.is_valid():
            order = serializer.save()
            clear_cart_cookie(response)
            response.data = {'detail': 'سفارش شما با موفقیت ثبت شد.', 'order_id': order.id}
            response.status_code = 201
            return response

        return Response(serializer.errors, status=400)

#-----------------------------------------------------------------------------------------------------------------------
#get-address-for-order
class UserAddressesForCheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated,IsOwnerObj]

    def get(self, request):
        user_addresses = Address.objects.filter(customer=request.user)
        serializer = AddressSerializer(user_addresses, many=True)
        return Response(serializer.data)
#-----------------------------------------------------------------------------------------------------------------------
                                        #template-view-order-panel
#-----------------------------------------------------------------------------------------------------------------------
#order-list-customer
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'customers/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')
#-----------------------------------------------------------------------------------------------------------------------
#order-detail-customer
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'customers/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.orderitem_set.select_related('product')
        return context
#-----------------------------------------------------------------------------------------------------------------------
#order-rating-list
class UserRatingsListView(LoginRequiredMixin,ListView):
    model = Rating
    template_name = 'customers/user_ratings_list.html'
    context_object_name = 'ratings'

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user, is_deleted=False)
#-----------------------------------------------------------------------------------------------------------------------