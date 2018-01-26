from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.core.urlresolvers import reverse

import stripe

from accounts.models import GuestModel


stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
# check for stripe integration
if stripe.api_key is None:
    raise NotImplementedError("STRIPE_SECRET_KEY must be set in the settings")

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

    # Alternatively, we can skip this method and do a separate import for Charge model in views
    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)

    def get_cards(self):
        return self.card_set.all()

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()

    def get_payment_method_url(self):
        return reverse('billing:payment-method')

    @property
    def has_card(self):
        return self.get_cards().exists()

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True, default=True)
        if default_cards.exists():
            return default_cards.first()
        return None


def user_created_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_post_save_receiver, sender=User)


def billing_profile_created_receiver(sender, instance, *args, **kwargs):
    # create a customer id for stripe
    # This is done as pre_save because we want to change customer_id if needed in future by just deleting
    # the id from admin panel and doing save and also delete the id from stripe panel.
    if not instance.customer_id and instance.email:
        customer = stripe.Customer.create(email=instance.email)
        instance.customer_id = customer.id

pre_save.connect(billing_profile_created_receiver, sender=BillingProfile)


class CardQuerySet(models.query.QuerySet):

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.get_or_new(request)
        return self.filter(billing_profile=billing_profile)


class CardManager(models.Manager):

    def get_queryset(self):
        return CardQuerySet(self.model, using=self._db)

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def all(self):  # overriding the default all() method
        return self.get_queryset().filter(active=True)

    def add_new(self, billing_profile, token):
        # create entry to stripe db
        customer = stripe.Customer.retrieve(billing_profile.customer_id)
        stripe_card_response = customer.sources.create(source=token)

        # create entry to django db
        if str(stripe_card_response.object) == 'card':
            new_card = self.model(
                billing_profile=billing_profile,
                stripe_id=stripe_card_response.id,
                brand=stripe_card_response.brand,
                country=stripe_card_response.country,
                exp_month=stripe_card_response.exp_month,
                exp_year=stripe_card_response.exp_year,
                last4=stripe_card_response.last4
            )
            new_card.save()
            return new_card
        return None


class Card(models.Model):
    """ We can fetch all the card data from the api just by using the stripe id, so we make it and the
    billing profile as required fields. We want to minimize the number of api calls made, thus we store
    some card data locally in the database. """
    billing_profile = models.ForeignKey(BillingProfile)
    stripe_id = models.CharField(max_length=120)
    brand = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    exp_month = models.IntegerField(blank=True, null=True)
    exp_year = models.IntegerField(blank=True, null=True)
    last4 = models.CharField(max_length=4, blank=True, null=True)
    default = models.BooleanField(default=True)  # default payment method
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CardManager()

    def __str__(self):
        return '{} {}'.format(self.brand, self.last4)

    def get_card_info(self):
        return '''{brand}<br/>xxxx xxxx xxxx {last4}<br/>Exp: {month}/{year}<br/>{country}<br/>
        '''.format(
            brand=self.brand,
            last4=self.last4,
            month=self.exp_month,
            year=self.exp_year,
            country=self.country
        )

    def set_default(self):
        qs = Card.objects.exclude(id=self.id)
        qs.update(default=False)
        self.default = True
        self.save()


def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile=billing_profile).exclude(id=instance.id)
        qs.update(default=False)

post_save.connect(new_card_post_save_receiver, sender=Card)


class ChargeManager(models.Manager):
    
    def do(self, billing_profile, order_obj, card=None):
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default=True)
            if cards.exists():
                card_obj = cards.first()
        # If after fetching card it still remains None
        if card_obj is None:
            return False, "No cards available"

        # create object in stripe
        charge = stripe.Charge.create(
            # amount has to be an integer in smallest currency unit (in this case - cents)
            # thus, cents = usd * 100
            amount=int(order_obj.total * 100),
            currency="usd",
            customer=billing_profile.customer_id,
            source=card_obj.stripe_id,
            description="charged $" + str(order_obj.total),
            metadata={'order_id': order_obj.order_id}
        )

        # create object in django database
        new_charge_obj = self.model(
            billing_profile=billing_profile,
            stripe_id=charge.id,
            paid=charge.paid,
            refunded=charge.refunded,
            outcome=charge.outcome,
            outcome_type=charge.outcome.get('type'),
            seller_message=charge.outcome.get('seller_message'),  # human-readable message
            risk_level=charge.outcome.get('risk_level')
        )
        new_charge_obj.save()
        return new_charge_obj.paid, new_charge_obj.seller_message


class Charge(models.Model):
    billing_profile = models.ForeignKey(BillingProfile)
    stripe_id = models.CharField(max_length=120)
    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    outcome = models.TextField(null=True, blank=True)  # Is a dictionary
    outcome_type = models.CharField(max_length=120, blank=True, null=True)
    seller_message = models.CharField(max_length=120, blank=True, null=True)
    risk_level = models.CharField(max_length=120, blank=True, null=True)

    objects = ChargeManager()

    def __str__(self):
        if not self.billing_profile.user:
            return 'guest - ' + str(self.paid)
        else:
            return self.billing_profile.user.email + ' - ' + str(self.paid)
