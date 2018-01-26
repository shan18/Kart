from django.contrib import admin

from .models import Product, ProductFile


class ProductFileInLine(admin.TabularInline):
    """
    Inline classes do not have a separate section of their own in the admin section.
    On viewing the product related to ProductFile model, it will contain a specific section related
    to inline in its detail page in the admin panel.

    This works in this way because there is a foreign key of Product inside ProductFile
    """
    model = ProductFile
    extra = 1  # by default only one file can be added (more can can still be added)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug', 'is_digital']
    inlines = [ProductFileInLine]

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
