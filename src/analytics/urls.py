from django.conf.urls import url, include

from .views import SalesView


urlpatterns = [
    url(r'^sales/$', SalesView.as_view(), name='sales')
]
