from django.conf.urls import url

from .views import (
        payment_method_view,
        payment_method_create_view,
        payment_method_reuse_view,
        PaymentMethodsListView
    )

urlpatterns = [
    url(r'^payment-method/$', payment_method_view, name='payment-method'),
    url(r'^payment-method/create/$', payment_method_create_view, name='payment-method-create-endpoint'),
    url(r'^payment-method/reuse/$', payment_method_reuse_view, name='payment-method-reuse-endpoint'),
    url(r'^payment-method/list/$', PaymentMethodsListView.as_view(), name='payment-method-list')
]
