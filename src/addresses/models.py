from django.db import models
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse

from billing.models import BillingProfile

ADDRESS_TYPES = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping')
)


class AddressQuerySet(models.query.QuerySet):
    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.get_or_new(request)
        return self.filter(billing_profile=billing_profile)


class AddressManger(models.Manager):
    def get_queryset(self):
        return AddressQuerySet(self.model, using=self._db)

    def by_request(self, request):
        return self.get_queryset().by_request(request)


class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile)
    address_type = models.CharField(max_length=120, choices=ADDRESS_TYPES)
    name = models.CharField(max_length=120)
    address_line_1 = models.CharField(max_length=120)
    address_line_2 = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    country = models.CharField(max_length=120, default='India')

    postal_code_regex = RegexValidator(regex=r'^\d{6}$', message="Postal code has only 6 digits")
    postal_code = models.CharField(validators=[postal_code_regex], max_length=120)

    phone_regex = RegexValidator(regex=r'^\d{9,15}$', message="Phone number must contain 10 digits")
    phone_number = models.CharField(validators=[phone_regex], max_length=10, blank=True)  # validators should be a list

    objects = AddressManger()

    def __str__(self):
        return str(self.billing_profile)

    def get_absolute_url(self):
        return reverse('address:update', kwargs={'address_id': self.pk})

    def get_delete_url(self):
        return reverse('address:delete', kwargs={'address_id': self.pk})

    def get_address(self):
        return "{line1}\n{line2}\n{city}\n{state}, {postal}\n{country}\nPhone number: {phone_number}".format(
            line1=self.address_line_1,
            line2=self.address_line_2 or "",
            city=self.city,
            state=self.state,
            postal=self.postal_code,
            country=self.country,
            phone_number=self.phone_number or "N/A"
        )

    def get_html_address(self):
        return '''{line1}<br/>{line2}<br/>{city}<br/>
            {state}, {postal}<br/>{country}<br/>Phone number: {phone_number}
        '''.format(
            name=self.name,
            line1=self.address_line_1,
            line2=self.address_line_2 or "",
            city=self.city,
            state=self.state,
            postal=self.postal_code,
            country=self.country,
            phone_number=self.phone_number or "N/A"
        )
