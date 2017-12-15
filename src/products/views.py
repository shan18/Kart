from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from .models import Product


""" Class Based Views
"""


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


""" Function Based Views
"""


def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, 'products/list.html', context)


def product_detail_view(request, pk, *args, **kwargs):
    # instance = Product.objects.get(pk=pk)
    instance = get_object_or_404(Product, pk=pk)    # If pk not in arg list, then pk=kwargs['pk']
    context = {
        'object': instance
    }
    return render(request, 'products/detail.html', context)
