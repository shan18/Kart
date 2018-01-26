from decimal import Decimal

from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.db.models.signals import pre_save, m2m_changed

from products.models import Product


User = settings.AUTH_USER_MODEL


class CartManager(models.Manager):

    def get_or_new(self, request):  # get existing cart else create new
        cart_id = request.session.get('cart_id', None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated() and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:  # This block will be executed when no such id exists or id cotntains non-numeric characters
            cart_obj = Cart.objects.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None and user.is_authenticated():
            user_obj = user
        return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)  # Non-logged in user can also create a cart
    products = models.ManyToManyField(Product, blank=True)  # Cart can be blank
    subtotal = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)  # stores the total of cart
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)  # stores the final price
    updated = models.DateTimeField(auto_now=True)  # Last updated time
    timestamp = models.DateTimeField(auto_now_add=True)  # Created time

    objects = CartManager()

    def __str__(self):
        return str(self.id)

    @property
    def has_tax(self):
        if self.subtotal != self.total:
            return True
        return False

    @property
    def is_digital(self):
        qs = self.products.filter(is_digital=False)
        if qs.exists():
            return False
        return True

    def get_tax(self):
        if self.has_tax:
            return self.total - self.subtotal
        return None

    def non_digital_products_total(self):
        qs = self.products.filter(is_digital=False)
        if qs.exists():
            total = qs.aggregate(Sum('price'))
            return total.get('price__sum')
        return 0


def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    # The following if block avoids calculations during pre actions
    if action == 'post_remove' or action == 'post_add' or action == 'post_clear':
        products = instance.products.all()
        total = 0
        for product in products:
            total += product.price
        if instance.subtotal != total:
            instance.subtotal = total
            instance.save()  # Since it is not a pre_save receiver, .save() is required

m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.products.through)


# This is used to include/deduct amount from subtotal like shipping charges, discounts e.t.c.
def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    if instance.subtotal > 0:
        instance.total = instance.subtotal
        # instance.total = Decimal(instance.subtotal) * Decimal(1.08)  # 8% tax
        # OR --> instance.total = float(instance.subtotal) * float(1.08)
    else:
        instance.total = 0.00

pre_save.connect(pre_save_cart_receiver, sender=Cart)
