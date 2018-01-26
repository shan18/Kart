from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin
from django.core.urlresolvers import reverse

from .models import GuestModel, EmailActivation
from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm
from kart.mixins import NextUrlMixin, RequestFormAttachMixin, AnonymousRequiredMixin


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


class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/detail_update_view.html'

    def get_object(self, **kwargs):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Change Your Account Details'
        return context

    def get_success_url(self):
        """
        This is used instead of using the class variable 'success_url' because class variable
        cannot be used with reverse
        """
        return reverse('account:home')


class AccountEmailActivateView(FormMixin, View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    key = None

    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
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
                    messages.success(request, mark_safe(msg))  # django's global messages
                    return redirect('login')
        context = {'form': self.get_form(), 'key': key}  # get_form() works because of the mixin
        return render(request, 'registration/activation_error.html', context)

    def post(self, request, *args, **kwargs):
        # create a form to receive an email
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = 'Activation link sent. Please check your email.'
        messages.success(self.request, msg)
        email = form.cleaned_data.get('email')
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation()
        return super(AccountEmailActivateView, self).form_valid(form)

    def form_invalid(self, form):
        """
        This method had to be explicitly written because this view uses the basic django "View" class.
        If it had used some other view like ListView etc. Django would have handled it automatically.
        """
        context = {'form': form, 'key': self.key}
        return render(self.request, 'registration/activation_error.html', context)


class GuestRegisterView(NextUrlMixin, RequestFormAttachMixin, CreateView):
    form_class = GuestForm
    default_next = '/register/'

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self, form):
        return redirect(self.default_next)

    # This function was removed because now form handles all this data
    # def form_valid(self, form):
    #     request = self.request
    #     email = form.cleaned_data.get('email')
    #     new_guest_obj = GuestModel.objects.create(email=email)
    #     request.session['guest_obj_id'] = new_guest_obj.id
    #     return redirect(self.get_next_url())


# def guest_register_view(request):
#     '''
#     Function based view for guest registration
#     '''
#     form = GuestForm(request.POST or None)
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         email = form.cleaned_data.get('email')
#         new_guest_obj = GuestModel.objects.create(email=email)
#         request.session['guest_obj_id'] = new_guest_obj.id
#         if is_safe_url(redirect_path, request.get_host()):
#             return redirect(redirect_path)
#         else:
#             return redirect('/register/')
#     return redirect('/register/')


class LoginView(AnonymousRequiredMixin, NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'
    default_next = '/'

    def form_valid(self, form):   # equivalent to "if form.is_valid()"
        request = self.request
        response = form.cleaned_data
        if not response.get('success'):
            messages.warning(self.request, mark_safe(response.get('message')))
            if request.is_ajax():
                return JsonResponse({
                    'success': response.get('success'), 'next_path': reverse('login')
                })
            return redirect('login')
        next_path = self.get_next_url()
        if request.is_ajax():
            return JsonResponse({
                'success': response.get('success'), 'next_path': next_path
            })
        return redirect(next_path)

    # These methods were removed because they were later used from within mixins
    # def get_form_kwargs(self):
    #     '''
    #     This method is overriden to send additional data from the view to the form.
    #     In function based view, this can be done as "form = LoginForm(request=request)"
    #     '''
    #     kwargs = super(LoginView, self).get_form_kwargs()
    #     kwargs['request'] = self.request
    #     return kwargs

    # def get_next_url(self):
    #     request = self.request
    #     next_ = request.GET.get('next')
    #     next_post = request.POST.get('next')
    #     redirect_path = next_ or next_post or None
    #     if is_safe_url(redirect_path, request.get_host()):
    #         return redirect_path
    #     else:
    #         return '/'


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
#     return render(request, 'accounts/login.html', context)


class RegisterView(AnonymousRequiredMixin, CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'

    def form_valid(self, form):
        super(RegisterView, self).form_valid(form)
        messages.success(self.request, 'Verification link sent! Please check your email.')
        if self.request.is_ajax():
            return JsonResponse({'success': True, 'next_path': self.success_url})
        return redirect(self.success_url)


# def register_page(request):
#     form = RegisterForm(request.POST or None)
#     context = {
#         "form": form
#     }
#     if form.is_valid():
#         form.save()  # Since we used a model form, we can save directly
#     return render(request, 'accounts/register.html', context)
