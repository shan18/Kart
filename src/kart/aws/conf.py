import datetime
import os

from kart import credentials


# AWS credentials
AWS_GROUP_NAME = os.environ.get('AWS_GROUP_NAME', credentials.AWS_GROUP_NAME)
AWS_USER_NAME = os.environ.get('AWS_USER_NAME', credentials.AWS_USER_NAME)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', credentials.AWS_ACCESS_KEY_ID)
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', credentials.AWS_SECRET_ACCESS_KEY)

AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = 'kart.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'kart.aws.utils.StaticRootS3BotoStorage'
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', credentials.AWS_STORAGE_BUCKET_NAME)
S3DIRECT_REGION = 'ap-southeast-1'
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = { 
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}

PROTECTED_DIR_NAME = 'protected'
PROTECTED_MEDIA_URL = '//%s.s3.amazonaws.com/%s/' %( AWS_STORAGE_BUCKET_NAME, PROTECTED_DIR_NAME)

# This specifies the time upto which a download link is valid. After the time expires, a new link is sent.
AWS_DOWNLOAD_EXPIRE = 5000 #(0ptional, in milliseconds)
