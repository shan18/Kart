from django.shortcuts import render, redirect

from .models import Cart
from products.models import Product
from orders.models import Order


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
        return render(request, 'carts/checkout.html', {'object': order_obj})
