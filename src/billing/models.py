from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from accounts.models import GuestModel


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


# Each registered user can have only one billing Profile
# Guest users can have multiple billing profiles
class BillingProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True)
    # OR --> user = models.ForeignKey(User, unique=True, null=True, blank=True) --> this can give some errors
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # customer_id for stripe or braintee

    objects = BillingProfileManager()

    def __str__(self):
        return self.email


def user_created_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_post_save_receiver, sender=User)
