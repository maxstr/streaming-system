#!/usr/bin/python

# Generating our website settings, replaces private/settings.py

import os

# Override the database settings to use a real database, only needed on
# production systems.
#---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' . (os.environ.get('DJANGO_DB_ENGINE') or 'postgresql_psycopg2'),
        'NAME': os.environ.get('DJANGO_DB_NAME') or  'website-run',
        'USER': os.environ.get('DJANGO_DB_USER') or '',
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD') or '',
        'HOST': os.environ.get('DJANGO_DB_HOST') or '',
        'PORT' : os.environ.get('DJANGO_DB_PORT') or '',
    }
}

SWITTER_CONSUMER_KEY = os.environ.get('SWITTER_CONSUMER_KEY') or '...'
SWITTER_CONSUMER_SECRET = os.environ.get('SWITTER_CONSUMER_SECRET') or '...'
SWITTER_ACCESS_TOKEN = os.environ.get('SWITTER_ACCESS_TOKEN') or '...'
SWITTER_ACCESS_TOKEN_SECRET = os.environ.get('SWITTER_ACCESS_TOKEN_SECRET') or '...'



