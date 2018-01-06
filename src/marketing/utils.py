import requests

from django.conf import settings


MAILCHIMP_API_KEY = getattr(settings, 'MAILCHIMP_API_KEY', None)
MAILCHIMP_DATA_CENTER = getattr(settings, 'MAILCHIMP_DATA_CENTER', None)
MAILCHIMP_EMAIL_LIST_ID = getattr(settings, 'MAILCHIMP_EMAIL_LIST_ID', None)


class Mailchimp(object):
    """class for handling mailchimp API calls: known as an API Wrapper"""
    def __init__(self, arg):
        super(Mailchimp, self).__init__()
        self.key = MAILCHIMP_API_KEY
        self.api_url = 'https://{dc}.api.mailchimp.com/3.0'.format(dc=MAILCHIMP_DATA_CENTER)
        self.list_id = MAILCHIMP_EMAIL_LIST_ID

    def check_subscription_status(self, email):
        # Things needed: endpoint(url), method, data, auth
        endpoint = self.api_url
        r = requests.get(endpoint, auth=("", self.key))
        return r.json()

    def add_email(self, email):
        # Things needed: endpoint(url), method, data, auth
        endpoint = self.api_url
        data = {
            'email': email
        }
        r = requests.get(endpoint, auth=("", self.key), data)
        return r.json()
