from django.conf.urls import url

from .views import (
        checkout_address_create_view,
        checkout_address_reuse_view,
        AddressListView,
        AddressUpdateView
    )

urlpatterns = [
    url(r'^checkout/create/$', checkout_address_create_view, name='checkout_address_create'),
    url(r'^checkout/reuse/$', checkout_address_reuse_view, name='checkout_address_reuse'),
    url(r'^list/$', AddressListView.as_view(), name='list'),
    url(r'^update/(?P<address_id>\d+)/$', AddressUpdateView.as_view(), name='update')
]
