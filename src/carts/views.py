from django.shortcuts import render, redirect

from .models import Cart
from products.models import Product
from orders.models import Order
from billing.models import BillingProfile
from accounts.models import GuestModel
from accounts.forms import LoginForm, GuestForm
from addresses.forms import AddressForm


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

    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()
    
    billing_profile, billing_profile_created = BillingProfile.objects.get_or_new(request)
    # if order related to the billing profile exists, use that. Else create one.
    if billing_profile is not None: # Without billing profile, order should not exist
        order_obj, order_obj_created = Order.objects.get_or_new(billing_profile, cart_obj)

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form
    }
    return render(request, 'carts/checkout.html', context)
