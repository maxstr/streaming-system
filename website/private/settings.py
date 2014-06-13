#!/usr/bin/python

# Generating our website settings, replaces private/settings.py

import os

# Override the database settings to use a real database, only needed on
# production systems.
#---------------------------------------------------------------------------
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'website-run',
#    }
#}

SWITTER_CONSUMER_KEY = os.environ.get('SWITTER_CONSUMER_KEY')
SWITTER_CONSUMER_SECRET = os.environ.get('SWITTER_CONSUMER_SECRET')
SWITTER_ACCESS_TOKEN = os.environ.get('SWITTER_ACCESS_TOKEN')
SWITTER_ACCESS_TOKEN_SECRET = os.environ.get('SWITTER_ACCESS_TOKEN_SECRET')
# If we are missing any, invalidate all
if (SWITTER_CONSUMER_KEY == None or SWITTER_CONSUMER_SECRET == None or SWITTER_ACCESS_TOKEN == None or SWITTER_ACCESS_TOKEN_SECRET == None):
    SWITTER_CONSUMER_KEY = "..."
    SWITTER_CONSUMER_SECRET = "..."
    SWITTER_ACCESS_TOKEN = "..."
    SWITTER_ACCESS_TOKEN_SECRET = "..."



