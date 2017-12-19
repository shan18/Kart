import os
import random

from django.db import models


def get_filename_extension(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    # print(instance)
    # print(filename)
    new_filename = random.randint(1, 5890349)
    name, ext = get_filename_extension(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return 'products/{new_filename}/{final_filename}'.format(
        new_filename=new_filename, final_filename=final_filename
    )


# Custom Model Manager, it extends the default one
class ProductManager(models.Manager):

    def featured(self):
        return self.get_queryset().filter(featured=True)
        
    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)  # equivalent to Product.objects.filter()
        if qs.count() == 1:
            return qs.first()
        return None


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured = models.BooleanField(default=False)

    objects = ProductManager()  # extends the default with the customized manager

    def __str__(self):  # For python 3
        return self.title

    def __unicode__(self):  # For python 2
        return self.title
