from django.conf.urls import url

from .views import (
        payment_method_view,
        payment_method_createview
    )
from products.views import UserProductHistoryView

urlpatterns = [
    url(r'^payment-method/$', payment_method_view, name='payment-method'),
    url(r'^payment-method/create/$', payment_method_createview, name='payment-method-endpoint')
]
