import os
from wsgiref.util import FileWrapper
from mimetypes import guess_type

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Product, ProductFile
from carts.models import Cart
from orders.models import ProductPurchase
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
        views = request.user.recently_viewed_items(model_class=Product, model_queryset=False, limit=11)
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
        """
        Exists in detail view.
        It is a custom model manager, it overrides the queryset attribute.
        """
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

    def get(self, request, *args, **kwargs):
        """ Get the file object to be downloaded """
        slug = kwargs.get('slug')
        pk = kwargs.get('pk')
        downloads_qs = ProductFile.objects.filter(pk=pk, product__slug=slug)
        if downloads_qs.count() != 1:
            raise Http404('Product Not Found')
        download_obj = downloads_qs.first()

        ''' Check permissions '''
        can_download = False
        user_ready = True
        if download_obj.user_required and not request.user.is_authenticated():
            user_ready = False

        purchased_products = Product.objects.none()
        if download_obj.free:
            can_download = True
        else:
            # not free
            purchased_products = ProductPurchase.objects.products_by_request(request)
            if download_obj.product in purchased_products:
                can_download = True

        if not can_download or not user_ready:
            messages.error(request, "You do not have access to download this item.")
            return redirect(download_obj.get_default_url())

        ''' Perform file download through AWS '''
        aws_filepath = download_obj.generate_download_url()
        return HttpResponseRedirect(aws_filepath)
        
        ''' Perform the file download through django '''
        # file_root = settings.PROTECTED_ROOT
        # filepath = download_obj.file.path  # .url /media/
        # final_filepath = os.path.join(file_root, filepath)
        # with open(final_filepath, 'rb') as f:
        #     wrapper = FileWrapper(f)
        #     mimetype = 'application/force-download'  # default MIME type for each file
        #     guessed_mimetype = guess_type(filepath)  # guess the MIME type for the given file
        #     if guessed_mimetype:
        #         mimetype = guessed_mimetype
        #     response = HttpResponse(wrapper, content_type=mimetype)
        #     response['Content-Disposition'] = 'attachment;filename=%s' %(download_obj.name)
        #     response['X-SendFile'] = str(download_obj.name)
        #     return response


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
        order = self.request.GET.get('orderby', '-featured')
        context['active_button'] = order
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        """
        Exists in list view.
        It is a custom model manager, it overrides the queryset attribute.
        """
        order = self.request.GET.get('orderby', '-featured')
        return Product.objects.all().order_by(order)


def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, 'products/list.html', context)
