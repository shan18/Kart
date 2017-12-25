from django.db import models
from django.db.models.signals import pre_save

from kart.utils import unique_order_id_generator
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

    def __str__(self):
        return self.order_id


# Generate order_id
def order_id_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)

pre_save.connect(order_id_pre_save_receiver, sender=Order)

# Calculate total
