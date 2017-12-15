from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    def __str__(self):  # For python 3
        return self.title

    def __unicode__(self):  # For python 2
        return self.title
