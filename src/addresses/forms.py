from django import forms

from .models import Address
from billing.models import BillingProfile


class AddressFormCheckout(forms.ModelForm):

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


class AddressForm(forms.ModelForm):
    name = forms.CharField(label='Name', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Name'}
    ))
    address_line_1 = forms.CharField(label='Address Line 1', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}
    ))
    address_line_2 = forms.CharField(label='Address Line 2', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}
    ))
    city = forms.CharField(label='City', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'City'}
    ))
    state = forms.CharField(label='State', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'State'}
    ))
    postal_code = forms.CharField(label='Postal Code', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Postal Code'}
    ))
    country = forms.CharField(label='Country', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Country'}
    ))
    phone_number = forms.CharField(label='Phone Number', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone Number'}
    ))

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
