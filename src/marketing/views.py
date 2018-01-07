from django.shortcuts import render, redirect
from django.views.generic import UpdateView
from django.http import HttpResponse
from django.contrib.messages.views import SuccessMessageMixin

from .models import MarketingPreference
from .forms import MarketingPreferenceUpdateForm


class MarketingPreferenceUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPreferenceUpdateForm
    template_name = 'base/forms.html'
    success_url = '/settings/email'  # we don't have get_absolute_url method, so we have to specify here
    success_message = 'Your email preferences have been updated!'

    def dispatch(self, *args, **kwargs):
        '''
        This function is the view part of the view. By overriding it, we first check
        some conditons and then only allow it to display the default view.
        '''
        user = self.request.user
        if not user.is_authenticated():
            # return HttpResponse('Not authorized', status=400)
            return redirect('/login/?next=/settings/email/')
        return super(MarketingPreferenceUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(MarketingPreferenceUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Update Email Preferences'
        return context

    def get_object(self):
        user = self.request.user
        obj, created = MarketingPreference.objects.get_or_create(user=user)
        return obj
