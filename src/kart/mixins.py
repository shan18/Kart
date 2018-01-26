from django.conf import settings
from django.utils.http import is_safe_url
from django.shortcuts import redirect


class RequestFormAttachMixin(object):

    def get_form_kwargs(self):
        """
        This method is overriden to send additional data from the view to the form.
        In function based view, this can be done as "form = LoginForm(request=request)"
        """
        kwargs = super(RequestFormAttachMixin, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class NextUrlMixin(object):
    default_next = '/'

    def get_next_url(self):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if is_safe_url(redirect_path, request.get_host()):
            return redirect_path
        return self.default_next


class AnonymousRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(getattr(settings, 'LOGIN_URL_REDIRECT', '/'))
        return super(AnonymousRequiredMixin, self).dispatch(request, *args, **kwargs)
