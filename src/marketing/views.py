from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import UpdateView, View
from django.http import HttpResponse
from django.contrib.messages.views import SuccessMessageMixin

from .models import MarketingPreference
from .forms import MarketingPreferenceUpdateForm
from .utils import Mailchimp
from .mixins import CsrfExemptMixin


MAILCHIMP_EMAIL_LIST_ID = getattr(settings, 'MAILCHIMP_EMAIL_LIST_ID', None)
if MAILCHIMP_EMAIL_LIST_ID is None:
    raise NotImplementedError("MAILCHIMP_EMAIL_LIST_ID must be set in the settings, something like us17")


class MarketingPreferenceUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPreferenceUpdateForm
    template_name = 'base/forms.html'
    success_url = '/settings/email'  # we don't have get_absolute_url method, so we have to specify here
    success_message = 'Your email preferences have been updated!'

    def dispatch(self, *args, **kwargs):
        """
        This function is the view part of the view. By overriding it, we first check
        some conditons and then only allow it to display the default view.
        """
        user = self.request.user
        if not user.is_authenticated():
            # return HttpResponse('Not authorized', status=400)
            return redirect('/login/?next=/settings/email/')
        return super(MarketingPreferenceUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(MarketingPreferenceUpdateView, self).get_context_data(*args, **kwargs)
        context['page_title'] = 'Email Preferences'
        context['title'] = 'Update Email Preferences'
        return context

    def get_object(self, **kwargs):
        user = self.request.user
        obj, created = MarketingPreference.objects.get_or_create(user=user)
        return obj


class MailchimpWebhookView(CsrfExemptMixin, View):
    """
    Class based view for the mailchimp webhook handler.
    Since it is only updating data, csrf can be exempted. In case of adding data, it can't be.
    """

    def post(self, request, *args, **kwargs):
        """
        Handles POST data
        """
        data = request.POST  # response from the webhook
        list_id = data['data[list_id]']
        if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
            hook_type = data['type']
            email = data['data[email]']
            response_status, response = Mailchimp().check_subscription_status(email)
            subscription_status = response['status']
            qs = MarketingPreference.objects.filter(user__email__iexact=email)
            if qs.exists():
                if subscription_status == 'subscribed':
                    qs.update(subscribed=True, mailchimp_subscribed=True, mailchimp_msg=str(data))
                elif subscription_status == 'unsubscribed':
                    qs.update(subscribed=False, mailchimp_subscribed=False, mailchimp_msg=str(data))
        return HttpResponse('Thank You!', status=200)


# def mailchimp_webhook_view(request):
#     """
#     Function based view for the mailchimp webhook handler
#     """
#     data = request.POST  # response from the webhook
#     list_id = data['data[list_id]']
#     if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
#         hook_type = data['type']
#         email = data['data[email]']
#         response_status, response = Mailchimp().check_subscription_status(email)
#         subscription_status = response['status']
#         qs = MarketingPreference.objects.filter(user__email__iexact=email)
#         if qs.exists():
#             if subscription_status == 'subscribed':
#                 qs.update(subscribed=True, mailchimp_subscribed=True, mailchimp_msg=str(data))
#             elif subscription_status == 'unsubscribed':
#                 qs.update(subscribed=False, mailchimp_subscribed=False, mailchimp_msg=str(data))
#     return HttpResponse('Thank You!', status=200)
