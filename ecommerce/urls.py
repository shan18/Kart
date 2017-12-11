from django.conf.urls import url
from django.contrib import admin

from .views import home_page

urlpatterns = [
    url(r'^$', home_page),
    url(r'^admin/', admin.site.urls),
]
