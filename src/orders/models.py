import math
import datetime

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Avg
from django.db.models.signals import pre_save, post_save
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone

from kart.utils import unique_order_id_generator, render_to_pdf
from carts.models import Cart
from billing.models import BillingProfile
from addresses.models import Address
from products.models import Product


ORDER_STATUS_CHOICES = (
    # (Database value, Display Value) # This separation is automatically done by the choices field in model
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded')
)


class OrderQuerySet(models.query.QuerySet):

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.get_or_new(request)
        return self.filter(billing_profile=billing_profile)

    def not_created(self):
        return self.exclude(status='created')

    def recent(self):
        return self.order_by('-updated', '-timestamp')

    def by_status(self, status='shipped'):
        return self.filter(status=status)

    def not_refunded(self):
        return self.exclude(status='refunded')

    def totals_data(self):
        return self.aggregate(Sum('total'), Avg('total'))

    def cart_data(self):
        return self.aggregate(
            Sum('cart__products__price'),
            Avg('cart__products__price'),
            Count('cart__products')
        )

    def by_date(self):
        now = timezone.now() - datetime.timedelta(days=7)
        return self.filter(updated__day__gte=now.day)

    def by_range(self, start_date, end_date=None):
        if not end_date:
            return self.filter(updated__gte=start_date)
        return self.filter(updated__gte=start_date).filter(updated__lte=end_date)

    def by_weeks_range(self, weeks_ago=1, number_of_weeks=2):
        if number_of_weeks > weeks_ago:
            number_of_weeks = weeks_ago
        days_ago_start = weeks_ago * 7
        days_ago_end = days_ago_start - number_of_weeks * 7
        start_date = timezone.now() - datetime.timedelta(days=days_ago_start)
        end_date = timezone.now() - datetime.timedelta(days=days_ago_end)
        return self.by_range(start_date, end_date)

    def get_sales_breakdown(self):
        recent = self.recent().not_refunded()
        recent_data = recent.totals_data()
        recent_cart_data = recent.cart_data()
        shipped = recent.by_status(status='shipped')
        shipped_data = shipped.totals_data()
        paid = recent.by_status(status='paid')
        paid_data = paid.totals_data()
        data = {
            'recent': recent,
            'recent_data': recent_data,
            'recent_cart_data': recent_cart_data,
            'shipped': shipped,
            'shipped_data': shipped_data,
            'paid': paid,
            'paid_data': paid_data
        }
        return data


class OrderManager(models.Manager):

    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def get_or_new(self, billing_profile, cart_obj):
        qs = self.get_queryset().filter(
            billing_profile=billing_profile, cart=cart_obj, active=True, status='created'
        )
        created = False
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(billing_profile=billing_profile, cart=cart_obj)
            created = True
        return obj, created


class Order(models.Model):
    order_id = models.CharField(max_length=120, blank=True)
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True)
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', null=True, blank=True, on_delete=models.SET_NULL)
    billing_address = models.ForeignKey(Address, related_name='billing_address', null=True, blank=True, on_delete=models.SET_NULL)
    cart = models.ForeignKey(Cart)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']

    def __str__(self):
        return self.order_id

    def get_absolute_url(self):
        return reverse('orders:detail', kwargs={'order_id': self.order_id})

    def get_invoice_url(self):
        return reverse('orders:detail-invoice', kwargs={'order_id': self.order_id})

    def get_status(self):
        if self.status == 'shipped':
            return 'Shipped'
        elif self.status == 'refunded':
            return 'Refunded'
        return 'Shipping Soon'

    def update_total(self):
        cart_non_digital_total = self.cart.non_digital_products_total()
        if cart_non_digital_total <= 15:
            self.shipping_total = 10.00
        new_total = math.fsum([self.cart.total, self.shipping_total])
        self.total = format(new_total, '.2f')
        self.save()
        return self.total

    def check_done(self):
        shipping_address_required = not self.cart.is_digital
        shipping_done = False
        if shipping_address_required:
            if self.shipping_address:
                shipping_done = True
            else:
                shipping_done = False
        else:
            shipping_done = True
        if self.billing_profile and shipping_done and self.billing_address and self.total > 0:
            return True
        return False

    def update_purchases(self):
        for product in self.cart.products.all():
            obj, created = ProductPurchase.objects.get_or_create(
                order_id=self.order_id,
                product=product,
                billing_profile=self.billing_profile
            )
        return ProductPurchase.objects.filter(order_id=self.order_id).count()

    def mark_paid(self):
        if self.status != 'paid':
            if self.check_done():
                self.status = 'paid'
                self.save()
                self.update_purchases()
        return self.status

    def generate_invoice(self):
        if self.status == 'paid' or self.status == 'shipped':
            invoice_data = {
                'object': self
            }
            if self.shipping_address is not None:
                invoice_data['shipping_address'] = self.shipping_address.get_address()
            invoice = render_to_pdf('order/invoice.html', invoice_data)
            return invoice
        return None

    def send_order_success_email(self):
        invoice = self.generate_invoice()
        if invoice is not None:
            context = {
                'order_id': self.order_id.upper()
            }
            subject = 'Your Order [{id}] with Kart has been confirmed.'.format(id=self.order_id.upper())
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient = [self.billing_profile.email]
            txt_ = get_template('order/order_success.txt').render(context)
            html_ = get_template('order/order_success.html').render(context)

            mail = EmailMultiAlternatives(subject, txt_, from_email, recipient)
            mail.attach_alternative(html_, "text/html")
            mail.attach('invoice.pdf', invoice.getvalue(), 'application/pdf')
            mail.send()


# Generate order_id
def order_id_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    # Since billing profile is associated to order during checkout, initially due to consecutive
    # login and logouts with guest or user, there can be multiple orders associated with a cart
    # so we set all those orders which are not associated to the billing profile to be inactive
    qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

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


class ProductPurchaseQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(refunded=False)

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.get_or_new(request)
        return self.filter(billing_profile=billing_profile)

    def digital(self):
        return self.filter(product__is_digital=True)


class ProductPurchaseManager(models.Manager):

    def get_queryset(self):
        return ProductPurchaseQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def digital(self):
        return self.get_queryset().active().digital()

    def products_by_id(self, request):
        qs = self.by_request(request).digital()
        ids_ = [x.product.id for x in qs]
        return ids_

    def products_by_request(self, request):
        ids_ = self.products_by_id(request)
        product_qs = Product.objects.filter(id__in=ids_).distinct()
        return product_qs


class ProductPurchase(models.Model):
    order_id = models.CharField(max_length=120)
    billing_profile = models.ForeignKey(BillingProfile)  # reverse lookup: all purchases from a single profile
    product = models.ForeignKey(Product)  # reverse lookup: total sales of a product
    refunded = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ProductPurchaseManager()

    def __str__(self):
        return self.product.title
