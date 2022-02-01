"""
Django settings for blight_fight project.

"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n!ri)qh6@-3&qgzj(&#6a#1-lsbb!j!vh^41ds5&d-f09nv=4*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CRISPY_FAIL_SILENTLY = not DEBUG

ALLOWED_HOSTS = []

INTERNAL_IPS = ['127.0.0.1',]

ADMINS = (('Chris Hartley', 'chris.hartley@renewindianapolis.org'),)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # required by allauth
    'django.contrib.gis',  # added 20150225
    'crispy_forms',  # added 20150225
    'django_tables2',  # added 20150225
    #'django_tables2_reports',  # added 20150225
    'django_filters',  # added 20150225
    'allauth',  # added 20150526
    'allauth.account',  # added 20150526
    #	'endless_pagination', # added 20150610 for old style map search.
    'django.contrib.humanize', # added 20150708 to format prices in template
    #    'formtools',    # added 20151028 to use form wizard for application form
    'ajaxuploader',
    'property_inventory',
    'annual_report_form',
    'property_inquiry',
    #'neighborhood_associations',
    'property_condition',
    'applications',
    'applicants',
    'user_files',
    'closings',
    'photos',
    'surplus',
    'univiewer',
    'epp_connector',
    'neighborhood_notifications',
    #'post_sale',#
    #'accella_records',
    'utils',
    #'debug_toolbar',#
    #'expense_tracking',#
    #'work_orders',#
    'market_activity',
    'commind',
    'ncst',
    'project_agreement_management',
)

# MIDDLEWARE_CLASSES = (
# #    'debug_toolbar.middleware.DebugToolbarMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django_tables2_reports.middleware.TableReportMiddleware',
# )

MIDDLEWARE = [
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'django_tables2_reports.middleware.TableReportMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'blight_fight.urls'

WSGI_APPLICATION = 'blight_fight.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'blight_fight',  # change this to a new db to prevent problems on dev server
        'USER': 'chris',
        'PASSWORD': 'chris',
        'HOST': '',
        'PORT': '',
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Indiana/Indianapolis'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static-collect")

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    '/home/chris/Projects/geodjango/static/',
)

# custom things added by Chris
CRISPY_TEMPLATE_PACK = 'bootstrap3'


# django-allauth required added 20150526
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
#                "django.core.context_processors.request",
                'django.template.context_processors.request',
                #'allauth.account.context_processors.account',
                #				'allauth.socialaccount.context_processors.socialaccount',
            ],
        },
    },
]

# django all-auth related
AUTHENTICATION_BACKENDS = (

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

)


LOGIN_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/accounts/profile'
LOGOUT_URL = '/accounts/logout'
#AUTH_USER_MODEL = 'applicants.ApplicantUser'
AUTH_PROFILE_MODULE = 'applicants.ApplicantProfile'

# django all-auth related
SITE_ID = 2

# set all-auth to use email as username
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USER_DISPLAY = lambda user: user.email
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_FORM_CLASS = 'applicants.forms.SignupForm'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Renew Indianapolis] '
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
#SOCIALACCOUNT_FORMS = {
#    'signup': 'applicants.forms.CustomSignupForm'
#}

# Email settings - for development. Typically over-written by production
# settings for production use
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# used by django-passwords
PASSWORD_COMPLEXITY = {  # You can omit any or all of these for no limit for that particular set
    "UPPER": 1,        # Uppercase
    "LOWER": 1,        # Lowercase
    "LETTERS": 0,       # Either uppercase or lowercase letters
    "DIGITS": 1,       # Digits
    "PUNCTUATION": 0,  # Punctuation (string.punctuation)
    "SPECIAL": 0,      # Not alphanumeric, space or punctuation character
    # Words (alphanumeric sequences separated by a whitespace or punctuation
    # character)
    "WORDS": 0
}


# media settings
MEDIA_ROOT = '/home/chris/Projects/geodjango/blight_fight/media/'
MEDIA_URL = '/media/'

FILE_UPLOAD_PERMISSIONS = 0o644

# stripe settings
# These key values are really set in settings_testing.py or settings_production.py
STRIPE_PUBLIC_API_KEY = ""
STRIPE_SECRET_API_KEY = ""

# mailchimp api settings
# These key values are really set in settings_testing.py or settings_production.py
MAILCHIMP_USERNAME = ''
MAILCHIMP_API_KEY = ''
MAILCHIMP_NEWSLETTER_ID = ''

# google api settings
# These key values are really set in settings_testing.py or settings_production.py
GOOGLE_API_TOKEN_LOCATION = ''
GOOGLE_STREETVIEW_API_KEY = ''
GOOGLE_STREETVIEW_API_KEY_SIGNING_SECRET = ''



#
COMPANY_SETTINGS = {
    'APPLICATION_CONTACT_NAME': 'Jeb Reece',
    'APPLICATION_CONTACT_EMAIL': 'landbank@renewindy.org',
    'APPLICATION_CONTACT_PHONE': '317-932-3770',
    'COMMERCIAL_CONTACT_NAME':'Jeb Reece',
    'COMMERCIAL_CONTACT_EMAIL': 'landbank@renewindy.org',
    'COMMERCIAL_CONTACT_PHONE': '317-932-3770',
    'SIDELOT_PROCESSING_FEE': 100,
    'SIDELOT_PROCESSING_STRIPE_FEE': 256, # new based on non-profit 2.2% + $0.30 rate
    'FDL_PROCESSING_FEE': 150,
    'FDL_PROCESSING_STRIPE_FEE': 360, # new based on non-profit 2.2% + $0.30 rate
    'STANDARD_PROCESSING_FEE': 250,
    'STANDARD_PROCESSING_STRIPE_FEE': 624, # new based on non-profit 2.2% + $0.30 rate
    'SIDELOT_PRICE': 750.00, # Regular sidelot price
    'AFFORDABLE_HOUSING_PROGRAM_LOT_FEE': 1500,
    'AFFORDABLE_HOUSING_PROGRAM_HOUSE_FEE': 3500,
    'RENEW_PA_RELEASE': 'landbank@renewindy.org',
    'CITY_PA_RELEASE': 'Matthew.Hostetler@indy.gov',
    'city_staff': (
        {'name': 'Ike McCoy', 'email': 'ike.mccoy@indy.gov'},
        {'name': 'Michelle Inabnit', 'email': 'Michelle.Inabnit@indy.gov'},
        ),
    'NCST_CONTACTS': ['realestateteam@renewindy.org',],
    'RENEW_REHAB_CONTACT': ['squick@renewindy.org','bburns@renewindy.org', 'bharris@renewindy.org'],
    'RENEW_OPERATIONS_MANAGER': ['bburns@renewindy.org',],
    'BLC_MANAGER': ['acernich@renewindy.org'],
    'RENEW_ACCOUNTANT': ['sumnersl@comcast.net'],
    'CONTACTS': (
        {'role': 'RENEW_REHAB_CONTACT', 'email': ['squick@renewindy.org','bburns@renewindy.org', 'bharris@renewindy.org']},
        {'role': 'NCST_CONTACTS', 'email': ['realestateteam@renewindy.org',],},
        {'role': 'RENEW_PA_RELEASE', 'email': ['jreece@@renewindy.org',],},
        {'role': 'CITY_PA_RELEASE', 'email': ['Matthew.Hostetler@indy.gov',],},
        {'role': 'RENEW_OPERATIONS_MANAGER', 'name': 'Brandi Burns', 'email': ['bburns@renewindy.org',],},


    ),
}

# This setting determins if property inquiries are allowed to be submitted
PROPERTY_INQUIRIES_ENABLED = True
# This setting sets if closing assignment notification emails are sent to city employees
SEND_CLOSING_ASSIGNMENT_EMAILS = True
CITY_PROPERTY_MANAGER_EMAIL = 'Michelle.Inabnit@indy.gov, ike.mccoy@indy.gov'
CITY_URBAN_GARDENING_MANAGER_EMAIL = 'matt.mosier@indy.gov' # notified in closings app if city owned urban garden license property sells
SEND_CITY_CLOSED_NOTIFICATION_EMAIL = True
BLC_MANAGER_EMAIL = 'chartley@renewindy.org'
SEND_BLC_ACTIVITY_NOTIFICATION_EMAIL = True
DEFAULT_FROM_EMAIL = 'info@renewindianapolis.org'
SMTP_PROVIDER = 'mailgun' # or gmail


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': False,
        },
         'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console',],#'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        # 'django': {
        #     'handlers': ['console'],
        #     'propagate': True,
        # },
    },
}


# Production settings are kept in a separate file, settings_production.py
# which overrides db, email, secret key, etc with production values
# Testing values are kept in settings_testing.py, for example stripe test api keys
try:
    from settings_testing import *
except ImportError:
    pass
try:
    from settings_production import *
except ImportError:
    pass

if DEBUG == False:
    if SMTP_PROVIDER == 'mailgun':
        from .settings_mailgun import *
    elif SMTP_PROVIDER == 'gmail':
        from .settings_gmail import *
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
