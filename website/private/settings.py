#!/usr/bin/python

# Generating our website settings, replaces private/settings.py

import os

# Override the database settings to use a real database, only needed on
# production systems.
#---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2'),
        'NAME': 'streamingsystem',
        'USER': 'streamingsystem',
        'PASSWORD': 'streamingsystem',
        'HOST': '',
        'PORT' : ''
    }
}

SWITTER_CONSUMER_KEY = os.environ.get('SWITTER_CONSUMER_KEY') or '...'
SWITTER_CONSUMER_SECRET = os.environ.get('SWITTER_CONSUMER_SECRET') or '...'
SWITTER_ACCESS_TOKEN = os.environ.get('SWITTER_ACCESS_TOKEN') or '...'
SWITTER_ACCESS_TOKEN_SECRET = os.environ.get('SWITTER_ACCESS_TOKEN_SECRET') or '...'



