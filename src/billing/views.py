from django.shortcuts import render

import stripe

from billing import credentials


stripe.api_key = credentials.SECRET_KEY
STRIPE_PUB_KEY = credentials.PUBLISH_KEY


def payment_method_view(request):
    if request.method == 'POST':
        print(request.POST)
    return render(request, 'billing/payment_method.html', {"publish_key": STRIPE_PUB_KEY})
