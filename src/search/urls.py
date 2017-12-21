from django.conf.urls import url

from .views import SearchListView


urlpatterns = [
    url(r'^$', SearchListView.as_view(), name='query'),
]
