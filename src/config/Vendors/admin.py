from django.contrib import admin

# Register your models here.
from django.contrib import admin

from Website.admin import ratingInline
from .models import Store, Employee, Product, Category, Discount

class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1
    fieldsets = (
        ('Employee', {
            'fields': ('user', 'store', 'position', 'is_deleted')
        }),
    )
    show_change_link = True

class DiscountInline(admin.TabularInline):
    model = Discount
    extra = 1
    fieldsets = (
        ('Employee', {
            'fields': ('name', 'value', 'type','store','start_at','finished_at','is_deleted','image')
        }),
    )
    show_change_link = True
# Register your models here.

class ProdeuctAdmin(admin.ModelAdmin):
    list_display = ['name', 'category__name', 'price', 'stock', 'store__name', 'store__owner__email']
    list_filter = ['category__name', 'store__name']
    search_fields = ['name', 'category__name']
    inlines = [ratingInline]

    fieldsets = (
        ('📝 اطلاعات اصلی', {
            'fields': ('name', 'price', 'store', 'category','discount')
        }),
        ('📷 محتوا', {
            'fields': ('image',)
        }),

    )


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fieldsets = (
        ('محصولات', {
            'fields': ('name', 'price', 'category', 'discount', 'variant', 'stock', 'image')
        }),
    )
    show_change_link = True


admin.site.register(Product, ProdeuctAdmin)


class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'owner', 'created_at', 'image', 'is_deleted']
    list_filter = ['is_deleted']
    search_fields = ['name']
    inlines = [ProductInline, EmployeeInline,DiscountInline]

    fieldsets = (
        ('📝 اطلاعات اصلی', {
            'fields': ('name', 'owner', 'address')
        }),
        ('📷 محتوا', {
            'fields': ('image',)
        }),

    )


admin.site.register(Store, StoreAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user__first_name', 'user__last_name', 'user__email', 'store__name', 'position', 'is_deleted']
    list_filter = ['position', 'store__name']
    search_fields = ['user__email', 'store__name']


    fieldsets = (
        ('📝 اطلاعات اصلی', {
            'fields': ('user__first_name', 'user__last_name', 'store__name', 'user__email', 'position',)
        }),

        ('⚙️ تنظیمات پیشرفته', {
            'fields': ('user__is_active', 'created_at', 'updated_at')
        }),
    )
admin.site.register(Employee, EmployeeAdmin)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent','is_deleted']
    list_filter = ['name', 'parent','is_deleted']
    search_fields = ['name', 'parent']
    inlines = [ProductInline]
    fieldsets = (
        ('📝 اطلاعات اصلی', {
            'fields': ('name', 'parent', 'is_deleted')
        }),

    )
admin.site.register(Category,CategoryAdmin)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'type', 'store__name', 'start_at', 'finished_at','is_deleted']
    list_filter = ['type', 'store__name','start_at','finished_at','is_deleted']
    search_fields = ['store__name', 'start_at']
    inlines = [ProductInline]
    fieldsets = (
        ('📝 اطلاعات اصلی', {
            'fields': ('name', 'value', 'type','store','start_at','finished_at','is_deleted')
        }),
        ('📷 محتوا', {
            'fields': ('image',)
        }),

    )
admin.site.register(Discount,DiscountAdmin)
