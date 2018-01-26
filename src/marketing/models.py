from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save

from .utils import Mailchimp
from accounts.models import GuestModel


User = settings.AUTH_USER_MODEL


class MarketingPreference(models.Model):
    user = models.OneToOneField(User)
    subscribed = models.BooleanField(default=True)
    mailchimp_subscribed = models.NullBooleanField(blank=True)
    mailchimp_msg = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


def make_marketing_pref_receiver(sender, instance, created, *args, **kwargs):
    """
    Create marketing preference when user is created
    """
    if created:
        MarketingPreference.objects.get_or_create(user=instance)

post_save.connect(make_marketing_pref_receiver, sender=User)


def marketing_preference_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        status_code, response_data = Mailchimp().subscribe(instance.user.email)

post_save.connect(marketing_preference_create_receiver, sender=MarketingPreference)


def marketing_preference_update_receiver(sender, instance, *args, **kwargs):
    """ When user changes the subscription status, it updates the mailchimp db
    """
    if instance.subscribed != instance.mailchimp_subscribed:
        if instance.subscribed:
            status_code, response_data = Mailchimp().subscribe(instance.user.email)
        else:
            status_code, response_data = Mailchimp().unsubscribe(instance.user.email)

        if response_data['status'] == 'subscribed':
            instance.subscribed = True
            instance.mailchimp_subscribed = True
        else:
            instance.subscribed = False
            instance.mailchimp_subscribed = False

        instance.mailchimp_msg = response_data

pre_save.connect(marketing_preference_update_receiver, sender=MarketingPreference)


class GuestModelMarketingPreference(models.Model):
    guest_user = models.OneToOneField(GuestModel)
    subscribed = models.BooleanField(default=True)
    mailchimp_subscribed = models.NullBooleanField(blank=True)
    mailchimp_msg = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.guest_user.email


def guest_marketing_pref_receiver(sender, instance, created, *args, **kwargs):
    """
    Create marketing preference when guest model is created
    """
    if created:
        GuestModelMarketingPreference.objects.get_or_create(guest_user=instance)

post_save.connect(guest_marketing_pref_receiver, sender=GuestModel)


def guest_marketing_preference_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        status_code, response_data = Mailchimp().subscribe(instance.guest_user.email)

post_save.connect(guest_marketing_preference_create_receiver, sender=GuestModelMarketingPreference)


def guest_marketing_preference_update_receiver(sender, instance, *args, **kwargs):
    """ When user changes the subscription status, it updates the mailchimp db
    """
    if instance.subscribed != instance.mailchimp_subscribed:
        if instance.subscribed:
            status_code, response_data = Mailchimp().subscribe(instance.guest_user.email)
        else:
            status_code, response_data = Mailchimp().unsubscribe(instance.guest_user.email)

        if response_data['status'] == 'subscribed':
            instance.subscribed = True
            instance.mailchimp_subscribed = True
        else:
            instance.subscribed = False
            instance.mailchimp_subscribed = False

        instance.mailchimp_msg = response_data

pre_save.connect(guest_marketing_preference_update_receiver, sender=GuestModelMarketingPreference)
