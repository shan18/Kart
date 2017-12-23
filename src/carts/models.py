from django.db import models
from django.conf import settings

from products.models import Product


User = settings.AUTH_USER_MODEL


class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)  # Non-logged in user can also create a cart
    products = models.ManyToManyField(Product, blank=True)  # Cart can be blank
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)  # Last updated time
    timestamp = models.DateTimeField(auto_now_add=True)  # Created time

    def __str__(self):
        return str(self.id)
