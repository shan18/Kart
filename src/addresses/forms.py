from django import forms

from .models import Address
from billing.models import BillingProfile


class AddressForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(AddressForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(AddressForm, self).save(commit=False)
        obj.billing_profile, created = BillingProfile.objects.get_or_new(self.request)
        obj.address_type = 'shipping'
        if commit:
            obj.save()
        return obj

    class Meta:
        model = Address
        fields = [
            # 'billing_profile',
            # 'address_type',
            'name',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'country',
            'postal_code',
            'phone_number'
        ]
