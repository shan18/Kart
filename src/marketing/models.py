from django.conf import settings
from django.db import models
from django.db.models.signals import post_save


User = settings.AUTH_USER_MODEL


class MarketingPreference(models.Model):
    user = models.OneToOneField(User)
    subscribed = models.BooleanField(default=True)
    mailchimp_msg = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


def make_marketing_pref_receiver(sender, instance, created, *args, **kwargs):
    '''
    Create marketing preference when user is created
    '''
    if created:
        MarketingPreference.objects.get_or_create(user=instance)

post_save.connect(make_marketing_pref_receiver, sender=User)


def marketing_preference_update_receiver(sender, instance, created, *args, **kwargs):
    # TODO: when user turns subscribe off, also update the mailchimp db
    if created:
        print('Add user to mailchimp')

post_save.connect(marketing_preference_update_receiver, sender=MarketingPreference)
