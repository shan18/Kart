from django import forms

from .models import MarketingPreference


class MarketingPreferenceUpdateForm(forms.ModelForm):
    subscribed = forms.BooleanField(label='Receive Marketing Emails?', required=False)

    class Meta:
        model = MarketingPreference
        fields = ['subscribed']
