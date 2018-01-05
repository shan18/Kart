from django.shortcuts import render, redirect
from django.http import JsonResponse

from .models import Cart
from products.models import Product
from orders.models import Order
from billing.models import BillingProfile
from accounts.models import GuestModel
from addresses.models import Address

from accounts.forms import LoginForm, GuestForm
from addresses.forms import AddressForm


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
            print("Show message to user, product gone?")
            return redirect('cart:home')
        cart_obj, new_obj = Cart.objects.get_or_new(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
        request.session['cart_items_number'] = cart_obj.products.count()

        if request.is_ajax():   # If ajax data, then send back form data in JSON
            print("Ajax request")
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

    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()

    shipping_address_id = request.session.get('shipping_address_id', None)
    billing_address_id = request.session.get('billing_address_id', None)
    
    billing_profile, billing_profile_created = BillingProfile.objects.get_or_new(request)
    address_qs = None
    # if order related to the billing profile exists, use that. Else create one.
    if billing_profile is not None: # Without billing profile, order should not exist
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

    if request.method == 'POST':
        if order_obj.check_done():
            did_charge_paid, charge_message = billing_profile.charge(order_obj)
            if did_charge_paid:
                order_obj.mark_paid()
                request.session['cart_items_number'] = 0
                del request.session['cart_id']
                return redirect('cart:success')
            else:
                print(charge_message)
                return redirect('cart:checkout')

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs
    }
    return render(request, 'carts/checkout.html', context)


def checkout_done(request):
    return render(request, 'carts/checkout_done.html', {})
