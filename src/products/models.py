import os
import random

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_save
from django.db.models import Q
from django.urls import reverse

from kart.aws.utils import ProtectedS3BotoStorage
from kart.aws.download.utils import AWSDownload
from kart.utils import unique_slug_generator, get_filename


def get_filename_extension(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1, 5890349)
    name, ext = get_filename_extension(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return 'products/{new_filename}/{final_filename}'.format(
        new_filename=new_filename, final_filename=final_filename
    )


# Custom QuerySet, it extends the default one
class ProductQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(active=True)

    def featured(self):  # Product.objects.all().featured()
        return self.filter(featured=True)

    def search(self, query):
        lookups = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(price__icontains=query) |
            Q(tag__title__icontains=query)
        )
        return self.filter(lookups).distinct()


# Custom Model Manager, it extends the default one
class ProductManager(models.Manager):

    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):  # Overrides Product.objects.all()
        return self.get_queryset().active()

    def featured(self):  # Product.objects.featured()
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)  # equivalent to Product.objects.filter()
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)


class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_digital = models.BooleanField(default=False)  # User Library

    objects = ProductManager()  # extends the default with the customized manager

    def get_absolute_url(self):
        # return '/products/{slug}'.format(slug=self.slug)
        return reverse("products:detail", kwargs={"slug": self.slug})

    def __str__(self):  # For python 3
        return self.title

    def __unicode__(self):  # For python 2
        return self.title

    @property
    def name(self):  # optional: with this Product.name will also work
        return self.title

    def get_downloads(self):
        qs = self.productfile_set.all().order_by('name')
        return qs


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, sender=Product)


def upload_product_file_location(instance, filename):
    # get the slug for the product
    slug = instance.product.slug
    if not slug:
        slug = unique_slug_generator(instance)

    # get the id
    id_ = instance.id
    if id_ is None:  # Newly uploaded files won't have an id, so get the new id by adding 1 to the last one.
        Klass = instance.__class__
        qs = Klass.objects.all().order_by('-pk')
        if qs.exists():
            id_ = qs.first().id + 1
        else:
            id_ = 0

    # specify the path
    location = 'products/{slug}/{id}/'.format(slug=slug, id=id_)
    return location + filename


class ProductFile(models.Model):
    product = models.ForeignKey(Product)
    file = models.FileField(
        upload_to=upload_product_file_location,
        storage=ProtectedS3BotoStorage()
        # storage=FileSystemStorage(location=settings.PROTECTED_ROOT) # store in local static_cdn
    )
    name = models.CharField(max_length=120, blank=True, null=True)
    free = models.BooleanField(default=False)  # default: purchase required
    user_required = models.BooleanField(default=False)  # default: user not required

    def __str__(self):
        return str(self.file.name)

    @property
    def display_name(self):
        original_name = get_filename(self.file.name)
        if self.name:
            return self.name
        return original_name

    def get_default_url(self):
        return self.product.get_absolute_url()

    def generate_download_url(self):
        """
        Generates the download url for downloads through aws.
        """
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        region = getattr(settings, 'S3DIRECT_REGION')
        if not bucket or not region or not access_key or not secret_key:
            return '/product-not-found/'  # TODO: raise custom 404 error

        PROTECTED_DIR_NAME = getattr(settings, 'PROTECTED_DIR_NAME', 'protected')
        # for aws, self.file is equivalent to self.file.path in local
        path = '{base}/{file_path}'.format(base=PROTECTED_DIR_NAME, file_path=str(self.file))

        aws_dl_object = AWSDownload(access_key, secret_key, bucket, region)
        file_url = aws_dl_object.generate_url(path, new_filename=self.display_name)
        return file_url

    def get_download_url(self):
        """
        Gives the download url when project is used in local settings
        """
        # return self.file.url  # This returns the path where file is stored
        return reverse('products:download', kwargs={
            'slug': self.product.slug, 'pk': self.pk
        })  # This returns the endpoint where file download is handled
