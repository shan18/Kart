from django.db import models

from carts.models import Cart


ORDER_STATUS_CHOICES = (
    # (Database value, Display Value) # This separation is automatically done by the choices field in model
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
    ('cancelled', 'Cancelled'),
    ('delivered', 'Delivered')
)


class Order(models.Model):
    order_id = models.CharField(max_length=120, blank=True)
    # billing_profile
    # billing_address
    # shipping_address
    cart = models.ForeignKey(Cart)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=50.00, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)


# Create order_id
# Calculate total
