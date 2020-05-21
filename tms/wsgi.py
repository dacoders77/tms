"""
WSGI config for tms project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""


import os
import sys
sys.path.insert(1, 'classes/')  # Path to DbLogger.py
from DbLogger import DbLogger
import logging
import time

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')

application = get_wsgi_application()

# Logging setup
if not os.path.exists("log"):
    os.makedirs("log")

time.strftime("pyibapi.%Y%m%d_%H%M%S.log")
recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'
timefmt = '%y%m%d_%H:%M:%S'

logdb = DbLogger()
logging.basicConfig(level=logging.DEBUG, format=recfmt, datefmt=timefmt)  # level=logging.INFO
logging.getLogger('').addHandler(logdb)

logging.getLogger('MY_LOGGER').setLevel('DEBUG')
logging.getLogger('MY_LOGGER').error('wsgi.py info text. Code: 34oozz')

