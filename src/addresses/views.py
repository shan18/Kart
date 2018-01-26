from django.shortcuts import redirect
from django.http import Http404
from django.utils.http import is_safe_url
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import AddressForm, AddressFormCheckout
from .models import Address
from billing.models import BillingProfile
from kart.mixins import RequestFormAttachMixin


def checkout_address_create_view(request):
    form = AddressFormCheckout(request.POST or None)
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None

    if form.is_valid():
        instance = form.save(commit=False)  # Model objects can be created directly from the ModelForm
        billing_profile, billing_profile_created = BillingProfile.objects.get_or_new(request)
        if billing_profile is not None:
            instance.billing_profile = billing_profile
            instance.address_type = request.POST.get('address_type', 'shipping')
            instance.save()
            request.session[instance.address_type + '_address_id'] = instance.id
        else:
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


class AddressListView(LoginRequiredMixin, ListView):
    template_name = 'addresses/list.html'

    def get_queryset(self):
        return Address.objects.by_request(self.request)

    def get_context_data(self, *args, **kwargs):
        context = super(AddressListView, self).get_context_data(*args, **kwargs)
        context['edit_address'] = True
        return context


class AddressCreateView(LoginRequiredMixin, RequestFormAttachMixin, CreateView):
    form_class = AddressForm
    template_name = 'addresses/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AddressCreateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Add New Address'
        context['button_text'] = 'Add'
        return context

    def form_valid(self, form):
        super(AddressCreateView, self).form_valid(form)
        messages.success(self.request, 'New address added successfully!')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('address:list')


class AddressUpdateView(LoginRequiredMixin, RequestFormAttachMixin, UpdateView):
    form_class = AddressForm
    template_name = 'addresses/detail.html'

    def get_object(self, **kwargs):
        qs = Address.objects.by_request(self.request).filter(pk=self.kwargs.get('address_id'))
        if qs.count() == 1:
            return qs.first()
        raise Http404

    def get_context_data(self, *args, **kwargs):
        context = super(AddressUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Edit Address'
        context['button_text'] = 'Update'
        return context

    def form_valid(self, form):
        super(AddressUpdateView, self).form_valid(form)
        messages.success(self.request, 'Address updated successfully!')
        return redirect(self.get_success_url())

    def get_success_url(self):
        """
        This is used instead of using the class variable 'success_url' because class variable
        cannot be used with reverse
        """
        return reverse('address:list')


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    success_message = "Address deleted successfully."

    def get_object(self, **kwargs):
        qs = Address.objects.by_request(self.request).filter(pk=self.kwargs.get('address_id'))
        if qs.count() == 1:
            return qs.first()
        raise Http404

    def delete(self, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(AddressDeleteView, self).delete(*args, **kwargs)

    def get_success_url(self):
        return reverse('address:list')
