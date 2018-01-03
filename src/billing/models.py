from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save

import stripe

from accounts.models import GuestModel
from billing import credentials


stripe.api_key = credentials.SECRET_KEY

User = settings.AUTH_USER_MODEL


class BillingProfileManager(models.Manager):

    def get_or_new(self, request):
        user = request.user
        guest_obj_id = request.session.get('guest_obj_id')
        obj = None
        created = False

        if user.is_authenticated():
            # Logged in user checkout; remebers payment stuff
            obj, created = self.model.objects.get_or_create(user=user, email=user.email)
        elif guest_obj_id is not None:
            # Guest user checkout; auto reloads payment stuff
            guest_obj = GuestModel.objects.get(id=guest_obj_id)
            obj, created = self.model.objects.get_or_create(email=guest_obj.email)
        else:
            pass

        return obj, created


# Each registered email can have only one billing Profile
class BillingProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True)
    # OR --> user = models.ForeignKey(User, unique=True, null=True, blank=True) --> this can give some errors
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=120, blank=True, null=True)  # for stripe

    objects = BillingProfileManager()

    def __str__(self):
        return self.email


def user_created_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_post_save_receiver, sender=User)


def billing_profile_created_receiver(sender, instance, *args, **kwargs):
    # create a customer id for stripe
    # This is done as pre_save because we want to change customer_id if needed in future by just deleting
    # the id from admin panel and doing save and also delete the id from stripe panel.
    if not instance.customer_id and instance.email:
        print("api request for stripe")
        customer = stripe.Customer.create(email=instance.email)
        instance.customer_id = customer.id
        print(customer)

pre_save.connect(billing_profile_created_receiver, sender=BillingProfile)
