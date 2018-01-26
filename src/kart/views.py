from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.template.loader import get_template

from .forms import ContactForm
from products.models import Product


def home_page(request):
    context = {
        'title': "Home",
        'featured_products': Product.objects.featured().order_by('-timestamp'),
        'digital_products': Product.objects.filter(is_digital=True)
    }
    if request.user.is_authenticated():
        context['recently_viewed'] = request.user.recently_viewed_items(
            model_class=Product, model_queryset=True, limit=5
        )
    return render(request, "home_page.html", context)


def about_page(request):
    context = {
        "title": "About",
        "content": "This is the about page."
    }
    return render(request, "about_page.html", context)


def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    context = {
        "title": "Contact Us",
        "content": "Please fill out this form to send us you query.",
        "form": contact_form
    }

    if contact_form.is_valid():
        data = contact_form.cleaned_data

        subject = 'Kart - Message from ' + data.get('email')
        txt_ = get_template('contact/message.txt').render(data)
        html_ = get_template('contact/message.html').render(data)
        from_email = 'Kart <' + data.get('email') + '>'
        recipient_list = [x[1] for x in settings.MANAGERS]
        send_mail(
            subject,
            txt_,
            from_email,
            recipient_list,
            html_message=html_,
            fail_silently=False
        )

        if request.is_ajax():
            return JsonResponse({"message": "Thank you for your response."})

    if contact_form.errors:     # If contact form has errors
        errors = contact_form.errors.as_json()  # convert to json
        if request.is_ajax():
            # Since data is already in json, we use HttpResponse
            return HttpResponse(errors, status=400, content_type='application/json')
            
    return render(request, "contact/view.html", context)


def home_page_old(request):
    return HttpResponse("<h1>Hello World!</h1>")
