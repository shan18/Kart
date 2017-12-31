from django.contrib import admin
from django.contrib.auth import get_user_model
# OR --> from .models import User

from .models import GuestModel


User = get_user_model()

class UserAdmin(admin.ModelAdmin):
    search_fields = ['email']   # Search users by email

    class Meta:
        model = User

admin.site.register(User, UserAdmin)


class GuestModelAdmin(admin.ModelAdmin):
    search_fields = ['email']   # Search users by email

    class Meta:
        model = GuestModel

admin.site.register(GuestModel, GuestModelAdmin)
