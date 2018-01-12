from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic  import ListView, DetailView

from .models import Order


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
