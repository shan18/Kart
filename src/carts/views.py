from django.shortcuts import render, redirect

from .models import Cart
from products.models import Product
from orders.models import Order
from billing.models import BillingProfile
from accounts.models import GuestModel
from accounts.forms import LoginForm, GuestForm


def cart_home(request):
    cart_obj, new_obj = Cart.objects.get_or_new(request)
    return render(request, 'carts/home.html', {'cart': cart_obj})


def cart_update(request):
    # print(request.POST)
    product_id = request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user, product gone?")
            return redirect('cart:home')
        cart_obj, new_obj = Cart.objects.get_or_new(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
        else:
            cart_obj.products.add(product_obj)
    request.session['cart_items_number'] = cart_obj.products.count()
    return redirect('cart:home')


def checkout_home(request):
    cart_obj, new_cart = Cart.objects.get_or_new(request)
    order_obj = None
    if new_cart or cart_obj.products.count() == 0:
        return redirect('cart:home')
    user = request.user
    billing_profile = None
    login_form = LoginForm()
    guest_form = GuestForm()
    guest_obj_id = request.session.get('guest_obj_id')
    if user.is_authenticated():
        billing_profile, billing_profile_created = BillingProfile.objects.get_or_create(
                                                       user=user, email=user.email
                                                   )
    elif guest_obj_id is not None:
        guest_obj = GuestModel.objects.get(id=guest_obj_id)
        billing_profile, billing_guest_profile_created = BillingProfile.objects.get_or_create(
                                                             email=guest_obj.email
                                                         )
    else:
        pass

    # Since billing profile is associated with order during checkout, initially due to consecutive
    # login and logouts with guest or user, there can be multiple orders associated with a cart
    # which don't have a billing profile or have the wrong profile, so we make all those orders
    # inactive and create a single active order associated with the cart and billing profile.
    if billing_profile is not None: # Without billing profile, order should not exist
        order_qs = Order.objects.filter(
            billing_profile=billing_profile, cart=cart_obj, active=True
        )
        if order_qs.count() == 1:
            order_obj = order_qs.first()
        else:
            old_order_qs = Order.objects.exclude(
                billing_profile=billing_profile
            ).filter(cart=cart_obj, active=True)
            if old_order_qs.exists():
                old_order_qs.update(active=False)
            order_obj = Order.objects.create(billing_profile=billing_profile, cart=cart_obj)

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form
    }
    return render(request, 'carts/checkout.html', context)
