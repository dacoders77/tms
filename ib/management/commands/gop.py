from django.core.management.base import BaseCommand, CommandError
from ib.models import Signal
from pprint import pprint

# A test command
# https://docs.djangoproject.com/en/2.1/howto/custom-management-commands/
class Command(BaseCommand):
    help = "Help text"

    def add_arguments(self, parser):
        parser.add_argument('id', type=int)

    def handle(self, *args, **options):
        # print('f')
        # for x in range(0, 5):
        #    self.stdout.write(str(x)) # Write to command's output
        record = Signal(
            url="www.ya.ru"
        )
        record.save()
        # pprint(Signal.objects.all())

        # print(str(options['id'])) # Works good


