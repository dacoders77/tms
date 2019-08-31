from django.core.management.base import BaseCommand, CommandError
from ib.models import Signal
import sys
sys.path.insert(1, 'classes/trade/') # Path to Trading app
from Trading import Trading
from Trading import TestApp

class Command(BaseCommand):
    help = "Help text"

    #def add_arguments(self, parser):
    #    parser.add_argument('id', type=int)

    def handle(self, *args, **options):
        print('co.py Method: handle')
        testApp = TestApp()
        testApp.main()





