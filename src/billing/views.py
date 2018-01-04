from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url

import stripe

from billing import credentials
from .models import BillingProfile, Card


stripe.api_key = credentials.SECRET_KEY
STRIPE_PUB_KEY = credentials.PUBLISH_KEY


def payment_method_view(request):
    # if request.user.is_authenticated():
    #     # since billing profile is created just after user creation, we can access it like this
    #     billing_profile = request.user.billing_profile
    #     my_customer_id = billing_profile.customer_id

    # this is to ensure that if a customer does not have a billing profile, he cannot access the payment page
    # for guests, their billing profile is created when they provide an email id
    billing_profile, billing_profile_created = BillingProfile.objects.get_or_new(request)
    if not billing_profile:
        return redirect("/cart")

    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_, request.get_host()):
        next_url = next_

    return render(request, 'billing/payment_method.html', {"publish_key": STRIPE_PUB_KEY, "next_url": next_url})


def payment_method_createview(request):
    # this method is accessed after submitting the data in stripe form
    # and it sends data back to the stripe ajax form handler
    if request.method == 'POST' and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.get_or_new(request)
        if not billing_profile:
            return HttpResponse({"message": "Cannot find this user"}, status=401)
        token = request.POST.get('token')
        if token is not None:
            customer = stripe.Customer.retrieve(billing_profile.customer_id)
            card_response = customer.sources.create(source=token)
            new_card_obj = Card.objects.add_new(billing_profile, card_response)
            print(new_card_obj)
        return JsonResponse({'message': 'Success! Your card was added.'})
    return HttpResponse('error', status=401)
