from django import forms
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import EmailActivation, GuestModel
from .signals import user_session_signal


User = get_user_model()


class ReactivateEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            register_link = reverse('register')
            msg = """This email does not exist.
            Would you like to <a href="{link}">register</a>?""".format(link=register_link)
            raise forms.ValidationError(mark_safe(msg))
        return email


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'is_active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserDetailChangeForm(forms.ModelForm):
    full_name = forms.CharField(label='Name', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['full_name']


class GuestForm(forms.ModelForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(
        attrs={'class': 'form-control my-2', 'placeholder': 'Email', 'id': 'guest-form-email-field'}
    ))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GuestForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        # Save the provided password in hashed format
        obj = super(GuestForm, self).save(commit=False)
        if commit:
            obj.save()
            request = self.request
            request.session['guest_obj_id'] = obj.id
        return obj
    
    class Meta:
        model = GuestModel
        fields = ['email']


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(
        attrs={'class': 'form-control my-2', 'placeholder': 'Email'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control my-2', 'placeholder': 'Password'}
    ))

    def __init__(self, request, *args, **kwargs):
        """
        This method was overwritten because some additional data was passed to the form from the view.
        """
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):  # This clean() method gets the entire form's data
        """
        With this function, the form itself handles the entire login process and only if the login
        is successful, it sends the data to the respective view.
        """
        request = self.request
        data = self.cleaned_data
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        response = {
            'success': False,
            'message': 'Login failed.'
        }

        user_qs = User.objects.filter(email=email, is_active=False)
        if user_qs.exists():
            # email is registered but not active
            link = reverse('account:resend-activation')
            reconfirm_msg = """Go to <a href="{resend_link}">resend confirmation email</a>.
            """.format(resend_link=link)
            is_email_confirmable = EmailActivation.objects.filter(email=email).confirmable().exists()
            email_activation_exists = EmailActivation.objects.email_exists(email).exists()
            if is_email_confirmable:
                msg1 = 'Please check your email to confirm your account or ' + reconfirm_msg.lower()
                response['message'] = msg1
                # raise forms.ValidationError(mark_safe(msg1))
            elif email_activation_exists:
                msg2 = 'Email not confirmed. ' + reconfirm_msg
                response['message'] = msg2
                # raise forms.ValidationError(mark_safe(msg2))
            else:
                response['message'] = 'This user is inactive.'
                # raise forms.ValidationError('This user is inactive.')
            return response

        user = authenticate(request, username=email, password=password)
        # If the is_active field is false, then the authenticate() method by default returns None
        if user is None:
            response['message'] = 'The username or the password is incorrect! Please try again.'
            # raise forms.ValidationError('Invalid credentials')
            return response
        login(request, user)
        response['success'] = True
        self.user = user  # Attach the form with the user so that the form can handle the model signals
        user_session_signal.send(user.__class__, instance=user, request=request)
        try:  # If user logs back in after registering as a guest, then delete the guest session
            del request.session['guest_obj_id']
        except:
            pass
        return response


class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    full_name = forms.CharField(label='Full Name', widget=forms.TextInput(
        attrs={'class': 'form-control my-2', 'placeholder': 'Full Name'}
    ))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(
        attrs={'class': 'form-control my-2', 'placeholder': 'Email'}
    ))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control my-2', 'placeholder': 'Password'}
    ))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control my-2', 'placeholder': 'Password'}
    ))

    class Meta:
        model = User
        fields = ('full_name', 'email')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False  # send email conformation via signals
        # email_obj = EmailActivation.objects.create(user=user)
        # email_obj.send_activation()
        if commit:
            user.save()
        return user
