from django.db import models
from django.contrib.auth.models import AbstractBaseUser


# Fields id, password and last_login are pre-defined in AbstractBaseUser
class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    # full_name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # staff (non superuser) user
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'    # email now acts as the username
    # USERNAME_FIELD and password are required by default
    REQUIRED_FIELDS = []    # ['full_name']  # these fields will be asked even when creating a superuser

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class GuestModel(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
