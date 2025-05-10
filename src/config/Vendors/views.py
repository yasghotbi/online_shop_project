from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Sum, Q, Avg
from django.db.models.functions import TruncMonth, TruncWeek
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, UpdateView,ListView,CreateView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from Accounts.models import CustomUser
from Accounts.serializers import CustomUserSerializer
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse, reverse_lazy
from Accounts.utils import  StoreAccessMixin
from Customers.models import OrderItem, Order
from Vendors.forms import ProductCreateForm, DiscountCreateForm, OrderStatusUpdateForm, ProductForm, UserProfileForm, \
    StoreForm
from Vendors.permissions import IsOwner
from Vendors.serializers import EmployeeSerializer, StoreSerializer, StoreSerializer2
from Vendors.models import Store, Employee, Product, Discount
from Vendors.utils import get_user_store
#-----------------------------------------------------------------------------------------------------------------------
                                #template-view-just-for-render
#_______________________________________________________________________________________________________________________
@login_required
def vendor_dashboard(request):
    store = get_user_store(request.user)
    if not store:
        return Http404("شما هیچ فروشگاهی ندارید.")
    return render(request, 'vendors/base.html', {'store': store})


def employee_register(request):
    return render(request, 'vendors/employee-register.html')
#-----------------------------------------------------------------------------------------------------------------------
                                #api-view-for-employee-record-just-by-owner
#-----------------------------------------------------------------------------------------------------------------------
@method_decorator(csrf_exempt, name='dispatch')
class RegisterEmployeeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "ثبت‌نام با موفقیت انجام شد.",
                "user_id": user.id,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#-----------------------------------------------------------------------------------------------------------------------
class EmployeeRecordView(APIView):
    permission_classes = [IsAuthenticated,IsOwner]

    def post(self, request):
        user_id = request.GET.get('user_id')
        employee_user = get_object_or_404(CustomUser, id=user_id)
        store_owner = request.user
        store = Store.objects.filter(owner=store_owner).first()

        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=employee_user, store=store)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#-----------------------------------------------------------------------------------------------------------------------
class StoreView(APIView):
    def get(self, request):
        stores = Store.objects.filter(is_deleted=False)
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = StoreSerializer2(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#-----------------------------------------------------------------------------------------------------------------------
                            #template-view-for-vendor-dashboard
#-----------------------------------------------------------------------------------------------------------------------
class StoreProfile(LoginRequiredMixin,StoreAccessMixin, PermissionRequiredMixin, DetailView):
    model=Store
    template_name = 'vendors/store-profile.html'
    context_object_name = 'store'
    permission_required = 'Vendors.view_store'

    def get_object(self, queryset=None):
        store = get_user_store(self.request.user)
        if store:
            return store
        raise Http404("شما اجازه دسترسی به این فروشگاه را ندارید.")
#-----------------------------------------------------------------------------------------------------------------------
#update-store-profile
class StoreUpdateView(LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin,UpdateView):
    model = Store
    template_name = 'vendors/profile-update.html'
    form_class = StoreForm
    context_object_name = 'store'
    permission_required = 'Vendors.change_store'


    def get_queryset(self):
        return Store.objects.filter(is_deleted=False)

    def get_success_url(self):
        return reverse_lazy('store-profile', kwargs={'pk': self.object.pk})

#-----------------------------------------------------------------------------------------------------------------------
#employee-list-by-store-staff
class EmployeeListView(LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin, ListView):
    model = Employee
    template_name = "vendors/employee-list.html"
    context_object_name = 'employees'
    permission_required = "Vendors.view_employee"


    def get_queryset(self):
        store = self.store
        return Employee.objects.filter(store=store, is_deleted=False)

#-----------------------------------------------------------------------------------------------------------------------
#employee-detail-by-store-staff
class EmployeeDetailView( LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin,DetailView):
    model = Employee
    template_name = "vendors/employee-detail.html"
    context_object_name = 'employee'
    permission_required = "Vendors.view_employee"

    def get_queryset(self):
        return Employee.objects.filter(store=self.store, is_deleted=False)
#-----------------------------------------------------------------------------------------------------------------------
#employee-update-by-manager-owner
class EmployeeUpdateView(LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin, UpdateView):
    model = Employee
    template_name = "vendors/update-employee.html"
    context_object_name = 'employee'
    fields = ['position','is_deleted']
    permission_required = "Vendors.change_employee"

    def get_queryset(self):
        return Employee.objects.filter(store=self.store, is_deleted=False)
    def get_success_url(self):
        return reverse('employee-list')
#-----------------------------------------------------------------------------------------------------------------------
#product-list-by-store-staff
class ProductListView(LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin,ListView):
    model = Product
    template_name = 'vendors/product-list.html'
    context_object_name = 'products'
    ordering = ['-created_at']
    permission_required = 'Vendors.view_product'

    def get_queryset(self):
        return Product.objects.filter(store=self.store, is_deleted=False)
#-----------------------------------------------------------------------------------------------------------------------
#product-detail-by-store-staff

class ProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, StoreAccessMixin, DetailView):
    model = Product
    template_name = "vendors/product-detail.html"
    context_object_name = 'product'
    permission_required = "Vendors.view_product"

    def get_queryset(self):
        return Product.objects.filter(store=self.store, is_deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # میانگین امتیاز (فقط امتیازهای معتبر و حذف‌نشده)
        average_rating = product.ratings.filter(
            is_deleted=False, rating__isnull=False
        ).aggregate(avg=Avg('rating'))['avg'] or 0

        # نظرات (فقط نظراتی که review نوشته شده و حذف‌نشده‌اند)
        reviews = product.ratings.filter(
            is_deleted=False, review__isnull=False
        ).exclude(review='').order_by('-created_at')

        context['average_rating'] = round(average_rating, 1)
        context['reviews'] = reviews
        return context

#-----------------------------------------------------------------------------------------------------------------------
#product-create-by-owner-manager
class ProductCreateView(LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin,CreateView):
    model = Product
    form_class = ProductCreateForm
    template_name = 'vendors/product-create.html'
    permission_required = "Vendors.add_product"

    def form_valid(self, form):
        form.instance.store = self.store
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('product-list-vendor')
#-----------------------------------------------------------------------------------------------------------------------
#product-update-by-owner-manager
class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, StoreAccessMixin, UpdateView):
    model = Product
    template_name = "vendors/product-update.html"
    context_object_name = 'product'
    form_class = ProductForm
    permission_required = "Vendors.change_product"

    def get_queryset(self):
        return Product.objects.filter(store=self.store, is_deleted=False)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'instance' in kwargs and kwargs['instance'].variant is None:
            kwargs['instance'].variant = {}
        return kwargs

    def form_valid(self, form):
        # Add debug print to verify form is being saved
        print("Form is valid, saving product...")
        return super().form_valid(form)


    def get_success_url(self):
        return reverse('product-list-vendor')
#-----------------------------------------------------------------------------------------------------------------------
#discount-list-by-store-staff

class DiscountListView(LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin,ListView):
    model = Discount
    template_name = 'vendors/discount-list.html'
    context_object_name = 'discounts'
    ordering = ['-created_at']
    permission_required = 'Vendors.view_discount'

    def get_queryset(self):
        return Discount.objects.filter(store=self.store, is_deleted=False)
#-----------------------------------------------------------------------------------------------------------------------
#discount-deatail-by-store-staff
class DiscountDetailView(LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin, DetailView):
    model = Discount
    template_name = "vendors/discount-detail.html"
    context_object_name = 'discount'
    permission_required = "Vendors.view_discount"

    def get_queryset(self):
        return Discount.objects.filter(store=self.store, is_deleted=False)
#-----------------------------------------------------------------------------------------------------------------------
#discount-create-by-manager-owner

class DiscountCreateView(LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin, CreateView):
    model = Discount
    form_class = DiscountCreateForm
    template_name = 'Vendors/discount-create.html'
    permission_required = "Vendors.add_discount"

    def form_valid(self, form):
        form.instance.store = self.store
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('discount-list')

#-----------------------------------------------------------------------------------------------------------------------
#discount-update-by-manager-owner

class DiscountUpdateView( LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin,UpdateView):
    model = Discount
    form_class = DiscountCreateForm
    template_name = "vendors/discount-update.html"
    context_object_name = 'discount'
    permission_required = "Vendors.change_discount"


    def get_queryset(self):
        return Discount.objects.filter(store=self.store, is_deleted=False)

    def get_success_url(self):
        return reverse('discount-list')

#-----------------------------------------------------------------------------------------------------------------------
#order-list-by-store-staff

class StoreOrdersView(LoginRequiredMixin,PermissionRequiredMixin,StoreAccessMixin, ListView):
    model = Order
    template_name = 'vendors/store_orders.html'
    context_object_name = 'orders'
    permission_required = "Customers.view_order"

    def get_queryset(self):

        return Order.objects.filter(orderitem__product__store=self.store).distinct().order_by('-created_at')
#-----------------------------------------------------------------------------------------------------------------------
#order-detail-by-store-staff
class StoreOrderDetailView(LoginRequiredMixin,StoreAccessMixin, DetailView):
    model = Order
    template_name = 'vendors/order_detail.html'
    context_object_name = 'order'
    permission_required = "Customers.view_order"

    def get_object(self, queryset=None):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_items = OrderItem.objects.filter(
            order=self.object,product__store=self.store)

        context['store_items'] = order_items
        return context
#-----------------------------------------------------------------------------------------------------------------------
#order-update-status-by-manager-owner
class StoreOrderStatusUpdateView(LoginRequiredMixin,StoreAccessMixin,UpdateView):
    model = Order
    form_class = OrderStatusUpdateForm
    template_name = 'vendors/order_update.html'
    context_object_name = 'order'
    permission_required = "Customers.change_order"

    def get_object(self, queryset=None):
        return get_object_or_404(Order, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('store-orders')
#-----------------------------------------------------------------------------------------------------------------------
class ProfileView( LoginRequiredMixin,StoreAccessMixin,DetailView):
    model = CustomUser
    template_name = "vendors/profile-user.html"
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return Employee.objects.get(user=self.request.user, store=self.store, is_deleted=False)
#-----------------------------------------------------------------------------------------------------------------------
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = "vendors/profile-update.html"
    context_object_name = 'user'


    def get_object(self, queryset=None):
        employee = Employee.objects.get(user=self.request.user, is_deleted=False)
        return employee.user

    def get_success_url(self):

        return reverse_lazy('profile', kwargs={'pk': self.object.pk})

#-----------------------------------------------------------------------------------------------------------------------
class DashboardSummaryAPIView(APIView):
    def get(self, request):
        now = timezone.now()
        start_of_month = now.replace(day=1)
        start_of_week = now - timedelta(days=7)
        today = now.date()

        store = Store.objects.filter(owner=request.user).first()
        if not store:
            return Response({'error': 'فروشگاهی برای این کاربر تعریف نشده است.'}, status=400)

        active_discounts = Discount.objects.filter(
            store=store,
            start_at__lte=now,
            finished_at__gte=now,
            is_deleted=False
        )

        discounted_products = Product.objects.filter(
            store=store,
            discount__in=active_discounts,
            is_deleted=False
        )

        pending_orders = Order.objects.filter(
            id__in=OrderItem.objects.filter(
                product__store=store
            ).values('order_id'),
            status='pending',
            is_paid=True
        ).distinct().count()

        active_discount_count = active_discounts.count()

        income_from_discounts = OrderItem.objects.filter(
            product__in=discounted_products,
            order__created_at__gte=start_of_month
        ).aggregate(total_income=Sum('price'))['total_income'] or 0

        online_employees = CustomUser.objects.filter(
            employee__store=store,
            role='employee',
            last_login__date=today
        ).values('id', 'first_name', 'last_name')

        new_users = CustomUser.objects.filter(
            store=store,
            role='user',
            date_joined__gte=start_of_week
        ).count()

        product_summary = Product.objects.filter(store=store, is_deleted=False).aggregate(
            total=Count('id'),
            in_stock=Count('id', filter=Q(stock__gt=0)),
            out_of_stock=Count('id', filter=Q(stock__lte=0))
        )

        monthly_income = OrderItem.objects.filter(
            product__store=store,
            order__created_at__gte=now - timedelta(days=365),
            product__discount__in=active_discounts
        ).annotate(
            month=TruncMonth('order__created_at')
        ).values('month').annotate(
            total_income=Sum('price')
        ).order_by('month')

        weekly_sales = OrderItem.objects.filter(
            product__store=store,
            order__created_at__gte=now - timedelta(weeks=12)
        ).annotate(
            week=TruncWeek('order__created_at')
        ).values('week').annotate(
            total_sold=Count('id')
        ).order_by('week')

        return Response({
            'pending_orders': pending_orders,
            'active_discount_count': active_discount_count,
            'income_from_discounts': income_from_discounts,
            'online_employees': list(online_employees),
            'new_users': new_users,
            'product_summary': product_summary,
            'weekly_sales': list(weekly_sales),
            'monthly_income': list(monthly_income),
        })

#-----------------------------------------------------------------------------------------------------------------------