import math

from django.db import models
from django.db.models.signals import pre_save, post_save

from kart.utils import unique_order_id_generator
from carts.models import Cart
from billing.models import BillingProfile


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
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True)
    # billing_address
    # shipping_address
    cart = models.ForeignKey(Cart)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=50.00, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.order_id

    def update_total(self):
        self.total = math.fsum([self.cart.total, self.shipping_total])
        self.save()
        return self.total


# Generate order_id
def order_id_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)

pre_save.connect(order_id_pre_save_receiver, sender=Order)


# It is used to update the order total when the cart is updated
# This method is executed only when changes occur in cart
# Here, instance = Cart
def cart_total_post_save_receiver(sender, instance, created, *args, **kwargs):
    if not created:  # 'created' checks if the cart has just been created
        # If the cart was just created then we don't execute the following code because
        # newly created cart won't have any order
        qs = Order.objects.filter(cart__id=instance.id)  # Orders associated with the cart
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()

post_save.connect(cart_total_post_save_receiver, sender=Cart)


# This method is executed when the order object is modified, whether it is directly or through the cart
def order_post_save_receiver(sender, instance, created, *args, **kwargs):
    # The check below ensures that the code here is executed only once when the order is created
    # For rest of the times, the order total should change only with cart updation
    # If the check is not present, this method is executed repeatedly and thus giving RecursionDepthError
    if created:  # If the order has just been created, then enter the block
        instance.update_total()

post_save.connect(order_post_save_receiver, sender=Order)
