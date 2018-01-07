from django.contrib import admin

from .models import MarketingPreference, GuestModelMarketingPreference


class MarketingPreferenceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'subscribed', 'updated']
    readonly_fields = ['mailchimp_msg', 'mailchimp_subscribed', 'timestamp', 'updated']

    class Meta:
        model = MarketingPreference
        fields = [
            'user', 'subscribed',
            'mailchimp_subscribed', 'mailchimp_msg', 'timestamp', 'updated'
        ]


admin.site.register(MarketingPreference, MarketingPreferenceAdmin)


class GuestModelMarketingPreferenceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'subscribed', 'updated']
    readonly_fields = ['mailchimp_msg', 'mailchimp_subscribed', 'timestamp', 'updated']

    class Meta:
        model = MarketingPreference
        fields = [
            'user', 'subscribed',
            'mailchimp_subscribed', 'mailchimp_msg', 'timestamp', 'updated'
        ]


admin.site.register(GuestModelMarketingPreference, GuestModelMarketingPreferenceAdmin)
