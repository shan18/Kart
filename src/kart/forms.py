from django import forms


class ContactForm(forms.Form):
    fullname = forms.CharField(label="Full Name", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Your full name"}
    ))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={"class": "form-control", "placeholder": "Your email"}
    ))
    content = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control", "placeholder": "Your message"}
    ))

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if not 'gmail.com' in email:
    #         raise forms.ValidationError('Email has to be gmail.com')
    #     return email

    # def clean_content(self):
    #     raise forms.ValidationError('Wrong content')
