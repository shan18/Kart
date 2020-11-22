"""
Store all sensitive data related to payments and other stuff in this file
"""


# django settings
SECRET_KEY = 'bebsv(pshw0%&i4k5w*bvgrx6o4ka&t+suwxami*2v7o_&xge1'

# email settings
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'sendgrid_api_key'

# stripe keys
STRIPE_SECRET_KEY = 'stripe_secret_key'
STRIPE_PUBLISH_KEY = 'stripe_publish_key'

# mailchimp keys
MAILCHIMP_API_KEY = 'mailchimp_api_key'
MAILCHIMP_DATA_CENTER = 'mail_chimp_data_center_code'
MAILCHIMP_EMAIL_LIST_ID = 'mailchimp_email_list_id'

# aws keys
AWS_GROUP_NAME = 'group_name'
AWS_USER_NAME = 'user_name'
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'
AWS_STORAGE_BUCKET_NAME = 'bucket_name'
