from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.core.urlresolvers import reverse

from django.core.mail import send_mail
from django.template.loader import get_template

from kart.utils import unique_key_generator


DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)


class UserManager(BaseUserManager):

    def create_user(self, email, full_name=None, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError("Users must have an email.")
        if not password:
            raise ValueError("Users must have a password")

        user_obj = self.model(
                       email=self.normalize_email(email),
                       full_name=full_name
                   )
        user_obj.set_password(password)    # Also used for changing the password
        user_obj.is_active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, full_name=None, password=None):
        user = self.create_user(
                   email,
                   full_name=full_name,
                   password=password,
                   is_staff=True
               )
        return user

    def create_superuser(self, email, full_name=None, password=None):
        user = self.create_user(
                   email,
                   full_name=full_name,
                   password=password,
                   is_staff=True,
                   is_admin=True
               )
        return user


class User(AbstractBaseUser):
    # Fields id, password and last_login are pre-defined in AbstractBaseUser
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    # is_active required by built in django password management
    is_active = models.BooleanField(default=True)  # can login
    staff = models.BooleanField(default=False)  # staff (non superuser) user
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'    # email now acts as the username
    # USERNAME_FIELD and password are required by default
    REQUIRED_FIELDS = []    # ['full_name']  # these fields will be asked even when creating a superuser

    objects = UserManager()

    def __str__(self):
        return self.email

    # The following functions have to included when using a custom user model

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, object=None):
        # Does the user have a specific permission?
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # Does the user have permissions to view the app `app_label`?
        # Simplest possible answer: Yes, always
        return True

    def recently_viewed_items(self, model_class, model_queryset, limit=None):
        qs = self.objectviewed_set.by_model(model_class, model_queryset=model_queryset)
        if limit:
            qs = qs[:limit]
        return qs

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    # commented out because is_active was required as an attribute by built in django password management
    # @property
    # def is_active(self):
    #     return self.active


class EmailActivationQuerySet(models.query.QuerySet):

    def confirmable(self):
        """
        Returns those emails which can be confirmed i.e. which are not activated and expired
        """
        now = timezone.now()
        start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        end_range = now
        return self.filter(
            activated=False,
            forced_expire=False
        ).filter(
            timestamp__gt=start_range,
            timestamp__lte=end_range
        )


class EmailActivationManager(models.Manager):

    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
        """
        EmailActivation is created when the user is created. When only EmailActivation is deleted, User object
        still remains i.e. email still exists. But this function will send nothing because for this function
        self.get_queryset() is None. So both user and EmailActivation should exist together for this to work.
        """
        return self.get_queryset().filter(
            Q(email=email) | Q(user__email=email)
        ).filter(activated=False)


class EmailActivation(models.Model):
    user = models.ForeignKey(User)
    email = models.EmailField()
    key = models.CharField(max_length=120, blank=True, null=True)  # activation key
    activated = models.BooleanField(default=False)
    forced_expire = models.BooleanField(default=False)  # link expired manually
    expires = models.IntegerField(default=7)  # automatic expire (after days)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        # A custom queryset was created because now a particular object can be checked directly
        # without first fetching the instance
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            # TODO: pre_save that user is activated (do something with this info)
            user = self.user
            user.is_active = True
            user.save()
            # TODO: post_save user activation signal (do something with this info)
            self.activated = True
            self.save()
            return True
        return False

    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation(self):
        if not self.activated and not self.forced_expire:
            if self.key:
                base_url = getattr(settings, 'HOST_SCHEME') + getattr(settings, 'BASE_URL')
                key_path = reverse('account:email-activate', kwargs={'key': self.key})
                path = '{base}{path}'.format(base=base_url, path=key_path)
                context = {
                    'path': path,
                    'email': self.email
                }
                txt_ = get_template('registration/emails/verify.txt').render(context)
                html_ = get_template('registration/emails/verify.html').render(context)
                subject = 'Kart - Verify your Account'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.email]
                sent_mail = send_mail(
                    subject,
                    txt_,  # If content_type is text/plain
                    from_email,
                    recipient_list,
                    html_message=html_,  # If content_type is text/html
                    fail_silently=False  # If false, then an email will be sent if error occurs while sending the email
                )
                return sent_mail
        return False


def pre_save_email_activation_receiver(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expire:
        if not instance.key:
            instance.key = unique_key_generator(instance)

pre_save.connect(pre_save_email_activation_receiver, sender=EmailActivation)


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        email_obj = EmailActivation.objects.create(user=instance, email=instance.email)
        email_obj.send_activation()

post_save.connect(post_save_user_create_receiver, sender=User)


class GuestModel(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
