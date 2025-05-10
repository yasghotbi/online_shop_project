from django.core.validators import MinValueValidator,MaxValueValidator
from django.db import models
from Accounts.models import CustomUser
from Customers.models import Order
from Vendors.models import Product


# Create your models here.
class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='ratings')
    rating = models.PositiveIntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'),
                                                  (5, '5 Stars')],blank=True,null=True)
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
#-----------------------------------------------------------------------------------------------------------------------


class Comment(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
#-----------------------------------------------------------------------------------------------------------------------