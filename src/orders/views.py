from django.shortcuts import render
from django.http import Http404, JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic  import ListView, DetailView, View
from django.template.loader import get_template

from .models import Order, ProductPurchase
from kart.utils import render_to_pdf


class OrderListView(LoginRequiredMixin, ListView):
    """
    default template name = 'order_list.html'
    """

    def get_queryset(self):
        return Order.objects.by_request(self.request).not_created()


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    default template name = 'order_detail.html'
    """

    def get_object(self):
        qs = Order.objects.by_request(self.request).filter(order_id=self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        raise Http404


class LibraryView(LoginRequiredMixin, ListView):
    template_name = 'orders/library.html'

    def get_queryset(self):
        return ProductPurchase.objects.products_by_request(self.request)


class VerifyOwnership(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            data = request.GET
            product_id = data.get('product_id', None)
            if product_id is not None:
                product_id = int(product_id)
                ownership_ids = ProductPurchase.objects.products_by_id(request)
                if product_id in ownership_ids:
                    return JsonResponse({'owner': True})
                return JsonResponse({'owner': False})
        raise Http404


class GenerateInvoicePDFView(View):

    def get(self, request, *args, **kwargs):
        qs = Order.objects.by_request(request).filter(order_id=self.kwargs.get('order_id'))
        if qs.count() == 1:
            order_obj = qs.first()
            invoice = order_obj.generate_invoice()
            if invoice:
                return HttpResponse(invoice, content_type='application/pdf')
        raise Http404
