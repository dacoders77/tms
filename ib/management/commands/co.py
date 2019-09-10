import django, time
django.setup()
from django.core.management.base import BaseCommand, CommandError
from pprint import pprint
from ib.models import Signal
import sys
sys.path.insert(1, 'classes/trade/') # Path to Trading app
from Trading import TestApp
#from Trading import Trading

from django.core import serializers
import json


class Command(BaseCommand):
    help = "Help text"

    def handle(self, *args, **options):
        print('co.py Method: handle')
        app = TestApp()
        app.main()















