from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .forms import AddressForm
from .models import Address
from billing.models import BillingProfile


def checkout_address_create_view(request):
    form = AddressForm(request.POST or None)
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None

    if form.is_valid():
        print(request.POST)

        instance = form.save(commit=False)  # Model objects can be created directly from the ModelForm
        billing_profile, billing_profile_created = BillingProfile.objects.get_or_new(request)
        if billing_profile is not None:
            instance.billing_profile = billing_profile
            instance.address_type = request.POST.get('address_type', 'shipping')
            instance.save()
            request.session[instance.address_type + '_address_id'] = instance.id
            print(instance.address_type + '_address_id')
        else:
            print('Error in saving the address')
            return redirect('cart:checkout')

        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)

    return redirect('cart:checkout')


def checkout_address_reuse_view(request):
    if request.user.is_authenticated():
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if request.method == 'POST':
            print(request.POST)
            address_id = request.POST.get('address_id', None)
            address_type = request.POST.get('address_type', 'shipping')
            billing_profile, billing_profile_created = BillingProfile.objects.get_or_new(request)
            if address_id is not None:
                qs = Address.objects.filter(billing_profile=billing_profile, id=address_id)
                if qs.exists():
                    request.session[address_type + '_address_id'] = address_id
                if is_safe_url(redirect_path, request.get_host()):
                    return redirect(redirect_path)
                    
    return redirect('cart:checkout')
