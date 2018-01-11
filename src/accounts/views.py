from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, FormView, DetailView, View
from django.core.urlresolvers import reverse

from .models import GuestModel, EmailActivation
from .forms import LoginForm, RegisterForm, GuestForm
from .signals import user_session_signal


# class LoginRequiredMixin(object):
#     """Custom login required mixin"""

#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class AccountHomeView(LoginRequiredMixin, DetailView):
    """Class based view for account home"""
    template_name = 'accounts/home.html'

    def get_object(self):
        return self.request.user

    # This can be used if we don't want to use a mixin
    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #     return super(AccountHomeView, self).dispatch(*args, **kwargs)


# @login_required  # automatically redirects to /accounts/login/?next=/some/path/ if not logged in
# def account_home_view(request):
#     '''
#     Function based view for account home
#     '''
#     return render(request, 'accounts/home.html', {})


class AccountEmailActivateView(View):

    def get(self, request, key, *args, **kwargs):
        qs = EmailActivation.objects.filter(key__iexact=key)
        confirm_qs = qs.confirmable()
        if confirm_qs.count() == 1:  # Not confirmed but confirmable
            obj = confirm_qs.first()
            obj.activate()
            messages.success(request, 'Your email has been confirmed! Please login to continue.')
            return redirect('login')
        else:
            activated_qs = qs.filter(activated=True)
            if activated_qs.exists():
                reset_link = reverse('password_reset')
                msg = """Your email has already been confirmed.
                Do you want to <a href="{link}">reset you password</a>?""".format(link=reset_link)
                messages.success(request, mark_safe(msg))
                return redirect('login')
        return render(request, 'registration/activation_error.html', {})

    def post(self, request, *args, **kwargs):
        pass


def guest_register_view(request):
    form = GuestForm(request.POST or None)
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        email = form.cleaned_data.get('email')
        new_guest_obj = GuestModel.objects.create(email=email)
        request.session['guest_obj_id'] = new_guest_obj.id
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect('/register/')
    return redirect('/register/')


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'

    def form_valid(self, form):   # equivalent to "if form.is_valid()"
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if not user.is_active:
                messages.error('The email is inactive')  # django global messages
                return super(LoginView, self).form_invalid(form)
            login(request, user)
            user_session_signal.send(user.__class__, instance=user, request=request)
            try:  # If user logs back in after registering as a guest, then delete the guest session
                del request.session['guest_obj_id']
            except:
                pass
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect('/')
        return super(LoginView, self).form_invalid(form)


# def login_page(request):
#     form = LoginForm(request.POST or None)
#     context = {
#         "form": form
#     }
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         username = form.cleaned_data.get('username')
#         password = form.cleaned_data.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             try:  # If user logs back in after registering as a guest, then delete the guest session
#                 del request.session['guest_obj_id']
#             except:
#                 pass
#             if is_safe_url(redirect_path, request.get_host()):
#                 return redirect(redirect_path)
#             else:
#                 return redirect('/')
#         else:
#             print("Error")
#     return render(request, 'accounts/login.html', context)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'


# def register_page(request):
#     form = RegisterForm(request.POST or None)
#     context = {
#         "form": form
#     }
#     if form.is_valid():
#         form.save()  # Since we used a model form, we can save directly
#     return render(request, 'accounts/register.html', context)
