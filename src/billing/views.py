from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

import stripe

from .models import BillingProfile, Card


stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
STRIPE_PUB_KEY = getattr(settings, 'STRIPE_PUBLISH_KEY', None)
# check for stripe integration
if stripe.api_key is None:
    raise NotImplementedError("STRIPE_SECRET_KEY must be set in the settings")
if STRIPE_PUB_KEY is None:
    raise NotImplementedError("STRIPE_PUB_KEY must be set in the settings")


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

    context = {
        "publish_key": STRIPE_PUB_KEY,
        "next_url": next_url
    }

    saved_cards_qs = Card.objects.filter(billing_profile=billing_profile)
    if saved_cards_qs.exists():
        context['saved_cards'] = saved_cards_qs

    return render(request, 'billing/payment_method.html', context)


def payment_method_create_view(request):
    # this method is accessed after submitting the data in stripe form
    # and it sends data back to the stripe ajax form handler
    if request.method == 'POST' and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.get_or_new(request)
        if not billing_profile:
            return HttpResponse({"message": "Cannot find this user"}, status=401)
        token = request.POST.get('token')
        if token is not None:
            # customer = stripe.Customer.retrieve(billing_profile.customer_id)
            # card_response = customer.sources.create(source=token)
            # new_card_obj = Card.objects.add_new(billing_profile, card_response)
            new_card_obj = Card.objects.add_new(billing_profile, token)
        return JsonResponse({'message': 'Success! Your card was added.'})
    return HttpResponse('error', status=401)


def payment_method_reuse_view(request):
    if request.user.is_authenticated():
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if request.method == 'POST':
            card_id = request.POST.get('card_id', None)
            if card_id is not None:
                card_qs = Card.objects.filter(pk=card_id)
                if card_qs.count() == 1:
                    card_qs.first().set_default()
                    request.session['card_id'] = card_id
                if is_safe_url(redirect_path, request.get_host()):
                    return redirect(redirect_path)

    return redirect('cart:checkout')


class PaymentMethodsListView(LoginRequiredMixin, ListView):
    template_name = 'billing/list.html'

    def get_queryset(self):
        return Card.objects.by_request(self.request)
