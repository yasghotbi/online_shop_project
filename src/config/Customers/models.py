from django.db import models
from Accounts.models import CustomUser
from Vendors.models import Product


class Address(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE,limit_choices_to={'role':'user'})
    title = models.CharField(max_length=120)
    address_text = models.TextField()
    post_code = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


    def __str__(self):
        return self.title

class Order(models.Model):
    STATUS_CHOICES = [('pending','pending'),('processing','Processing'),('delivered','Delivered')]
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE,limit_choices_to={'role':'user'})
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.is_paid = True#---->????
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orderitems')
    quantity = models.IntegerField()
    price = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.pk:
            product = self.product
            if product.stock < self.quantity:
                raise ValueError("موجودی کافی نیست.")
            product.stock -= self.quantity
            product.save()
            if not self.price:
                self.price = product.price
        super().save(*args, **kwargs)

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [('online','Online'),('cod','Cod'),('wallet','Wallet')]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    paid_at = models.DateTimeField(auto_now_add=True)

