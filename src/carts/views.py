from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.core.urlresolvers import reverse

import stripe

from .models import Cart
from products.models import Product
from orders.models import Order
from billing.models import BillingProfile, Card
from addresses.models import Address

from accounts.forms import LoginForm, GuestForm
from addresses.forms import AddressFormCheckout


stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
STRIPE_PUB_KEY = getattr(settings, 'STRIPE_PUBLISH_KEY', None)
# check for stripe integration
if stripe.api_key is None:
    raise NotImplementedError("STRIPE_SECRET_KEY must be set in the settings")
if STRIPE_PUB_KEY is None:
    raise NotImplementedError("STRIPE_PUB_KEY must be set in the settings")


def cart_home_api_view(request):
    cart_obj, new_obj = Cart.objects.get_or_new(request)
    products = [{
        'id': x.id,
        'url': x.get_absolute_url(),
        'name': x.name,
        'price': x.price
    } for x in cart_obj.products.all()]
    # We can't directly pass the object to ajax, we need to convert it to JSON format
    cart_data = {"products": products, "subtotal": cart_obj.subtotal, "total": cart_obj.total}
    return JsonResponse(cart_data)


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
            messages.error(request, "Oops! The product does not exist.")
            return redirect('cart:home')

        # guests cannot buy digital products
        if product_obj.is_digital and not request.user.is_authenticated():
            if request.is_ajax():
                json_data = {       # Additional data we want to send along with the form data
                    "noLoginDigital": True
                }
                return JsonResponse(json_data, status=200)
            messages.error(request, "You must login, in order to purchase any digital items!")
            return redirect('login')

        cart_obj, new_obj = Cart.objects.get_or_new(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
        request.session['cart_items_number'] = cart_obj.products.count()

        if request.is_ajax():   # If ajax data, then send back form data in JSON
            json_data = {       # Additional data we want to send along with the form data
                "added": added,
                "cartItemCount": cart_obj.products.count()
            }
            return JsonResponse(json_data, status=200)  # JsonResponse sends only form data if no parameters are given
            # return JsonResponse({"message": "Error 400"}, status=400)
    return redirect('cart:home')


def checkout_home(request):

    cart_obj, new_cart = Cart.objects.get_or_new(request)
    order_obj = None
    if new_cart or cart_obj.products.count() == 0:
        return redirect('cart:home')

    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressFormCheckout()

    shipping_address_required = not cart_obj.is_digital

    shipping_address_id = request.session.get('shipping_address_id', None)
    billing_address_id = request.session.get('billing_address_id', None)
    
    billing_profile, billing_profile_created = BillingProfile.objects.get_or_new(request)
    address_qs = None
    has_card = False
    # if order related to the billing profile exists, use that. Else create one.
    if billing_profile is not None:  # Without billing profile, order should not exist
        if request.user.is_authenticated():
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.get_or_new(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session['shipping_address_id']
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session['billing_address_id']
        if shipping_address_id or billing_address_id:
            order_obj.save()
        has_card = billing_profile.has_card

    if request.method == 'POST':
        if order_obj.check_done():

            card_obj = None
            card_id = request.session.get('card_id', None)
            if card_id:
                card_obj = Card.objects.get(id=card_id)
                del request.session['card_id']

            did_charge_paid, charge_message = billing_profile.charge(order_obj, card_obj)
            if did_charge_paid:
                order_obj.mark_paid()  # acts as a signal when order is paid for
                order_obj.send_order_success_email()
                request.session['cart_items_number'] = 0
                del request.session['cart_id']
                if not billing_profile.user:
                    billing_profile.set_cards_inactive()
                request.session['checkout_home'] = True
                try:  # delete guest session
                    del request.session['guest_obj_id']
                except:
                    pass
                if request.is_ajax():
                    return JsonResponse({'next_path': reverse('cart:success')})
                return redirect('cart:success')
            else:
                if request.is_ajax():
                    return JsonResponse({'next_path': reverse('cart:checkout')})
                return redirect('cart:checkout')

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
        "has_card": has_card,
        "publish_key": STRIPE_PUB_KEY,
        "shipping_address_required": shipping_address_required
    }
    return render(request, 'carts/checkout.html', context)


def checkout_done(request):
    if request.session.get('checkout_home'):
        del request.session['checkout_home']
        return render(request, 'carts/checkout_done.html', {})
    raise Http404
