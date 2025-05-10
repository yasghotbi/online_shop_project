from django.contrib import admin
from Website.models import Rating

class ratingInline(admin.TabularInline):
    model = Rating
    extra = 1
    fieldsets = (
        ('rating', {
            'fields': ('user', 'product', 'rating', 'review')
        }),
    )
    show_change_link = True

class RatingAdmin(admin.ModelAdmin):
    list_display = ['user__email', 'product__name', 'product__store', 'rating', 'created_at']
    list_filter = ['product__name','product__store']
    search_fields = ['product__name','product__store']


    fieldsets = (
        ('📝 اطلاعات اصلی', {
            'fields': ('user', 'product', 'rating','review',)
        }),

    )
admin.site.register(Rating, RatingAdmin)