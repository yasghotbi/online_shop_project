import json

from django import forms

from Accounts.models import CustomUser
from Customers.models import Order
from .models import Product, Discount, Store


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'discount', 'image']

class DiscountCreateForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['name', 'value', 'type', 'start_at', 'finished_at', 'is_deleted','image']
        widgets = {
            'start_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'finished_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'discount', 'stock', 'variant', 'image', 'is_deleted']
        widgets = {
            'variant': forms.Textarea(attrs={'class': 'json-field'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.variant is None:
            self.initial['variant'] = '{}'

    def clean_variant(self):
        variant = self.cleaned_data.get('variant')

        if isinstance(variant, str):
            variant = variant.strip()
            if variant == '':
                return {}
            try:
                return json.loads(variant)
            except json.JSONDecodeError:
                raise forms.ValidationError("فرمت ویژگی‌ها معتبر نیست. لطفاً JSON صحیح وارد کنید.")


        elif isinstance(variant, dict):
            return variant

        return {}


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        labels = {
            'username': 'نام کاربری',
            'email': 'ایمیل',
            'phone_number': 'شماره تلفن'
        }
        help_texts = {
            'username': 'نام کاربری شما برای ورود به سیستم استفاده می‌شود',
            'email': 'ایمیل معتبر خود را وارد کنید',
            'phone_number': 'شماره همراه با پیش‌شماره (مثال: 09123456789)'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['email'].required = True




class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'address', 'image', 'image2']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }