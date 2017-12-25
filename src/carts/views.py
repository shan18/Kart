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
    if new_cart or cart_obj.products.count() == 0:
        return redirect('cart:home')
    else:
        order_obj, new_order = Order.objects.get_or_create(cart=cart_obj)  # In-built function
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

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form
    }
    return render(request, 'carts/checkout.html', context)
