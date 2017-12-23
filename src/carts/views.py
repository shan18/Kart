from django.shortcuts import render

from .models import Cart


def cart_create(user=None):
    cart_obj = Cart.objects.create(user=None)
    print('New Cart created')
    return cart_obj


def cart_home(request):
    cart_id = request.session.get('cart_id', None)
    qs = Cart.objects.filter(id=cart_id)
    if qs.count() == 1:
        print('Cart ID exists')
        cart_obj = qs.first()
    else:  # This block will be executed when no such id exists or id cotntains non-numeric characters
        cart_obj = cart_create()
        request.session['cart_id'] = cart_obj.id
    return render(request, 'carts/home.html', {})
