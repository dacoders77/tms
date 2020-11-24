import django, time
django.setup()
from django.core.management.base import BaseCommand, CommandError
from pprint import pprint
from ib.models import Signal
import sys
sys.path.insert(1, 'classes/trade/') # Path to Trading app
from Trading import TestApp


from django.core import serializers
import json

from ib.models import Log

class Command(BaseCommand):
    help = "Help text"

    def handle(self, *args, **options):
        print('co.py Method: handle')



        r = Log()
        r.source = 'started running'
        try:
            r.save()
        except:
            print('DbLogger.py update model exception catch. Code: 6677hh')

        app = TestApp()
        app.main()















