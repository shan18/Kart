from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import Http404

from .models import Product


""" Class Based Views """


class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'products/list.html'

    # use this to check which key in context has the data, then use that in the template
    # def get_context_data(self, *args, **kwargs):
    #     context = super(ProductListView, self).get_context_data(*args, **kwargs)
    #     print(context)
    #     return(context)


class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = 'products/detail.html'


""" Function Based Views """


def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, 'products/list.html', context)


def product_detail_view(request, pk, *args, **kwargs):
    # instance = get_object_or_404(Product, pk=pk)    # If pk not in arg list, then pk=kwargs['pk']

    # This is the close manual version of the get_object_or_404 method
    # try:
    #     instance = Product.objects.get(id=pk)
    # except Product.DoesNotExist:
    #     print("No such product exists.")
    #     raise Http404("Product dosen't exist")
    # except:
    #     print('huh!')

    # If multiple entries exist with same title/pk, we can manually handle such errors with this method
    # For default actions, we can directly use get_object_or_404 method for this.
    # queryset = Product.objects.filter(id=pk)
    # if queryset.exists() and queryset.count() == 1:  # len(queryset)
    #     instance = queryset.first()
    # else:
    #     raise Http404("Product dosen't exist")

    # Above approach can be done using custom model managers too
    instance = Product.objects.get_by_id(pk)
    if instance is None:
        raise Http404("Product dosen't exist")

    context = {
        'object': instance
    }

    return render(request, 'products/detail.html', context)
