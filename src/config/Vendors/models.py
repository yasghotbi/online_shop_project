from contextlib import nullcontext

from django.db import models
from  Accounts.models import CustomUser
from Accounts.utils import update_user_group
from django.contrib.auth.models import Group
from django.utils import timezone

# Create your models here.
class Store(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    image2 = models.ImageField(upload_to='uploads/', null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.id:
            self.owner.role = 'owner'
            self.owner.save()
            update_user_group(user=self.owner)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Employee(models.Model):
    POSITION_CHOICES = [('manager', 'Manager'), ('operator', 'Operator')]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='operator')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.user.role = 'employee'
            self.user.save()
            update_user_group(user=self.user)
        super().save(*args, **kwargs)
        manager_group, created = Group.objects.get_or_create(name='manager')
        if self.position == 'manager':
            if not self.user.groups.filter(name='manager').exists():
                self.user.groups.add(manager_group)
        else:
            self.user.groups.remove(manager_group)

    def __str__(self):
        return f"{self.user.first_name}-{self.user.last_name}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Discount(models.Model):
    TYPE_CHOICES = [('cash','Cash'),('percentage','Percentage')]
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='percentage')
    store = models.ForeignKey(Store,on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    store = models.ForeignKey(Store, on_delete=models.CASCADE,related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name="products")
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE,null=True,blank=True)
    price = models.IntegerField()
    variant = models.JSONField(default=dict)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)#---> stock or quantidy



    @property
    def price_after_discount(self):
        if not self.discount or self.discount.is_deleted:
            return self.price
        now = timezone.now()
        if now < self.discount.start_at or now > self.discount.finished_at:
            return self.price
        if self.discount.type == 'cash':
            return max(self.price - float(self.discount.value), 0)

        return int(self.price * (1 - self.discount.value / 100))


    def __str__(self):
        return f'{self.name}---{self.store.name}'




