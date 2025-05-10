from django.contrib import admin

from Accounts.models import CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone_number', 'first_name', 'last_name', 'is_superuser']
    list_filter = ['email','phone_number','role']
    search_fields = ['email','phone_number']

admin.site.register(CustomUser, CustomUserAdmin)