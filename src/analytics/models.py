from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


User = settings.AUTH_USER_MODEL


class ObjectViewed(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)  # null/blank is enabled because we also want to track guest
    # We can use an IpField but then various systems have different permissions and we would have to handle all that
    ip_address = models.CharField(max_length=220, blank=True, null=True)

    # The following three generic fields can be replaced by a field for each specific model or by a single url field
    content_type = models.ForeignKey(ContentType)  # Has the content of the specified model
    object_id = models.PositiveIntegerField()  # Has the object id for model specified above
    content_object = GenericForeignKey('content_type', 'object_id')  # Has the instance of the object of model selected

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s viewed on %s' % (self.content_object, self.timestamp)

    class Meta:
        ordering = ['-timestamp']  # Most recently saved showed first
        verbose_name = 'Object viewed'
        verbose_name_plural = 'Objects viewed'
