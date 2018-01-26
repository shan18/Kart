import requests
import json
import re
import hashlib

from django.conf import settings


MAILCHIMP_API_KEY = getattr(settings, 'MAILCHIMP_API_KEY', None)
if MAILCHIMP_API_KEY is None:
    raise NotImplementedError("MAILCHIMP_API_KEY must be set in the settings")

MAILCHIMP_DATA_CENTER = getattr(settings, 'MAILCHIMP_DATA_CENTER', None)
if MAILCHIMP_DATA_CENTER is None:
    raise NotImplementedError("MAILCHIMP_DATA_CENTER must be set in the settings, something like us17")

MAILCHIMP_EMAIL_LIST_ID = getattr(settings, 'MAILCHIMP_EMAIL_LIST_ID', None)
if MAILCHIMP_EMAIL_LIST_ID is None:
    raise NotImplementedError("MAILCHIMP_EMAIL_LIST_ID must be set in the settings, something like us17")


def check_email(email):
    if not re.match(r'.+@.+\..+', email):
        raise ValueError('String passes is not a valid email address')
    return email


def get_subscriber_hash(member_email):
    """
    This makes a email hash which is required by the Mailchimp API
    """
    # .encode() returns a bytes representation of the Unicode string
    member_email = check_email(member_email).lower().encode()
    m = hashlib.md5(member_email)
    return m.hexdigest()


class Mailchimp(object):
    """ Class for handling mailchimp API calls: known as an API Wrapper
        See docs: https://developer.mailchimp.com/documentation/mailchimp/reference/lists/members/
    """
    def __init__(self):
        super(Mailchimp, self).__init__()
        self.key = MAILCHIMP_API_KEY
        self.api_url = 'https://{dc}.api.mailchimp.com/3.0'.format(dc=MAILCHIMP_DATA_CENTER)
        self.list_id = MAILCHIMP_EMAIL_LIST_ID
        self.list_endpoint = '{api_url}/lists/{list_id}'.format(
                                 api_url=self.api_url,
                                 list_id=self.list_id
                             )

    def get_members_endpoint(self):
        return self.list_endpoint + '/members/'

    def check_valid_status(self, status):
        # pending means user did not confirm his email id
        # cleaned means email bounced and has been removed from the list
        choices = ['subscribed', 'unsubscribed', 'cleaned', 'pending']
        if status not in choices:
            raise ValueError('Not a valid email status choice')
        return status

    def check_subscription_status(self, email):
        # Things needed: endpoint(url), method, data, auth
        hashed_email = get_subscriber_hash(email)
        # it is unsafe to send data in url directly, so the api uses the hashed form for security
        endpoint = self.get_members_endpoint() + '/' + hashed_email
        r = requests.get(endpoint, auth=("", self.key))
        # we send the status_code in order to check for errors in django while making the call
        return r.status_code, r.json()

    def change_subscription_status(self, email, status='unsubscribed'):
        # Things needed: endpoint(url), method, data, auth
        hashed_email = get_subscriber_hash(email)
        # it is unsafe to send data in url directly, so the api uses the hashed form for security
        endpoint = self.get_members_endpoint() + '/' + hashed_email
        data = {
            'email_address': email,
            'status': self.check_valid_status(status)
        }
        r = requests.put(endpoint, auth=("", self.key), data=json.dumps(data))
        return r.status_code, r.json()

    def subscribe(self, email):
        return self.change_subscription_status(email, status='subscribed')

    def unsubscribe(self, email):
        return self.change_subscription_status(email, status='unsubscribed')

    def pending(self, email):
        return self.change_subscription_status(email, status='pending')

    def add_email(self, email):
        # Things needed: endpoint(url), method, data, auth
        """ The PUT method in change_subscription_status can add an email to the list directly if
            it does not exists. So with that, this function has become redundant. """
        status = self.check_valid_status('subscribed')
        data = {
            'email_address': email,
            'status': status
        }
        endpoint = self.get_members_endpoint()
        r = requests.post(endpoint, auth=("", self.key), data=json.dumps(data))
        return r.status_code, r.json()
