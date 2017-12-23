from django.db import models
from django.conf import settings

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

    def new(self, user=None):
        user_obj = None
        if user is not None and user.is_authenticated():
            user_obj = user
        return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)  # Non-logged in user can also create a cart
    products = models.ManyToManyField(Product, blank=True)  # Cart can be blank
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)  # Last updated time
    timestamp = models.DateTimeField(auto_now_add=True)  # Created time

    objects = CartManager()

    def __str__(self):
        return str(self.id)
