from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.http import Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Product, ProductFile
from carts.models import Cart
from analytics.mixins import ObjectViewedMixin


class UserProductHistoryView(LoginRequiredMixin, ListView):
    template_name = 'products/user-history.html'

    def get_context_data(self, *args, **kwargs):
        context = super(UserProductHistoryView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.get_or_new(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):  # Custom Model Manager, overrides the queryset attribute
        request = self.request
        views = request.user.objectviewed_set.by_model(Product, model_queryset=False)
        return views


class ProductFeaturedListView(ListView):
    template_name = 'products/list.html'

    def get_queryset(self, *args, **kwargs):   # Custom Model Manager
        request = self.request
        return Product.objects.all().featured()


class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all().featured()
    template_name = 'products/featured-detail.html'


class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = 'products/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.get_or_new(self.request)
        context['cart'] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        '''
        Exists in detail view.
        It is a custom model manager, it overrides the queryset attribute.
        '''
        request = self.request
        slug = self.kwargs.get('slug')
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("No such product exists")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug, active=True)
            return qs.first()
        except:
            raise Http404("Huh!!")

        # Calling the custom signal
        # object_viewed_signal.send(instance.__class__, instance=instance, request=request)
        return instance


class ProductDownloadView(View):

    def get(self, *args, **kwargs):
        slug = kwargs.get('slug')
        pk = kwargs.get('pk')
        downloads_qs = ProductFile.objects.filter(pk=pk, product__slug=slug)
        if downloads_qs.count() != 1:
            raise Http404('Product Not Found')
        download_obj = downloads_qs.first()
        response = HttpResponse(download_obj.get_download_url())
        return response


class ProductDetailView(ObjectViewedMixin, DetailView):
    # queryset = Product.objects.all()
    template_name = 'products/detail.html'

    def get_object(self, *args, **kwargs):  # custom model manager
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product doesn't exist")
        return instance

    # def get_queryset(self, *args, **kwargs):   # Another version of Custom Model Manager
    #     request = self.request
    #     pk = self.kwargs.get('pk')
    #     return Product.objects.filter(pk=pk)


def product_detail_view(request, pk, *args, **kwargs):
    # instance = get_object_or_404(Product, pk=pk)    # If pk not in arg list, then pk=kwargs['pk']

    # This is the close manual version of the get_object_or_404 method
    # try:
    #     instance = Product.objects.get(id=pk)
    # except Product.DoesNotExist:
    #     print("No such product exists.")
    #     raise Http404("Product doesn't exist")
    # except:
    #     print('huh!')

    # If multiple entries exist with same title/pk, we can manually handle such errors with this method
    # For default actions, we can directly use get_object_or_404 method for this.
    # queryset = Product.objects.filter(id=pk)
    # if queryset.exists() and queryset.count() == 1:  # len(queryset)
    #     instance = queryset.first()
    # else:
    #     raise Http404("Product doesn't exist")

    # Above approach can be done using custom model managers too
    instance = Product.objects.get_by_id(pk)
    if instance is None:
        raise Http404("Product doesn't exist")

    context = {
        'object': instance
    }

    return render(request, 'products/detail.html', context)


class ProductListView(ListView):
    # queryset = Product.objects.all()
    template_name = 'products/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.get_or_new(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        '''
        Exists in list view.
        It is a custom model manager, it overrides the queryset attribute.
        '''
        request = self.request
        return Product.objects.all()


def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, 'products/list.html', context)
