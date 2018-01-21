from django.conf.urls import url

from .views import (
        OrderListView,
        OrderDetailView,
        GenerateInvoicePDFView,
        VerifyOwnership
    )
from products.views import UserProductHistoryView

urlpatterns = [
    url(r'^$', OrderListView.as_view(), name='list'),
    url(r'^(?P<order_id>[0-9A-Za-z]+)/$', OrderDetailView.as_view(), name='detail'),
    url(r'^(?P<order_id>[0-9A-Za-z]+)/invoice/$', GenerateInvoicePDFView.as_view(), name='detail-invoice'),
    url(r'^endpoint/verify/ownership/$', VerifyOwnership.as_view(), name='verify-ownership')
]
