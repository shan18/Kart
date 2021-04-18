from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView

from .views import home_page, about_page, contact_page
from accounts.views import LoginView, RegisterView, GuestRegisterView
from carts.views import cart_home_api_view
from orders.views import LibraryView
from marketing.views import MarketingPreferenceUpdateView, MailchimpWebhookView

urlpatterns = [
    url(r'^$', home_page, name='home'),
    url(r'^about/$', about_page, name='about'),
    # url(r'^contact/$', contact_page, name='contact'),
    # url(r'^accounts/login/$', RedirectView.as_view(url='/login')),
    url(r'^account/', include('accounts.urls', namespace='account')),
    url(r'^accounts/', include('accounts.passwords.urls')),
    url(r'^accounts/$', RedirectView.as_view(url='/account')),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^register/guest/$', GuestRegisterView.as_view(), name='guest_register'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^address/', include('addresses.urls', namespace='address')),
    url(r'^api/cart/$', cart_home_api_view, name='api-cart'),
    url(r'^billing/', include('billing.urls', namespace='billing')),
    url(r'^analytics/', include('analytics.urls', namespace='analytics')),
    url(r'^settings/$', RedirectView.as_view(url='/account')),
    url(r'^settings/email/$', MarketingPreferenceUpdateView.as_view(), name='marketing-preferences'),
    url(r'^webhooks/mailchimp/$', MailchimpWebhookView.as_view(), name='webhooks-mailchimp'),
    url(r'^products/', include('products.urls', namespace='products')),
    url(r'^library/$', LibraryView.as_view(), name='library'),
    url(r'^orders/', include('orders.urls', namespace='orders')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^cart/', include('carts.urls', namespace='cart')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
