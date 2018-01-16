from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from orders.models import Order


class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return render(self.request, '403.html', {})
        return super(SalesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(SalesView, self).get_context_data(*args, **kwargs)
        qs = Order.objects.all()
        context['orders'] = qs

        context['recent_orders'] = qs.recent().not_refunded()[:7]
        context['recent_orders_data'] = context['recent_orders'].totals_data()
        context['recent_cart_data'] = context['recent_orders'].cart_data()

        context['shipped_orders'] = qs.recent().not_refunded().by_status(status='shipped')[:2]
        context['shipped_orders_data'] = context['shipped_orders'].totals_data()

        context['paid_orders'] = qs.recent().not_refunded().by_status(status='paid')[:5]
        context['paid_orders_data'] = context['paid_orders'].totals_data()

        return context
