from django.core.management.base import BaseCommand, CommandError
from ib.models import Signal
import logging
import json


class Request(BaseCommand):

    @staticmethod
    def store(payload):
        data = json.loads(payload)
        record = Signal(
            status = "new",
            request_payload = payload,
            # date=time.strftime('%Y-%m-%d %H:%M:%S'),
            url=data['url'],
            # symbol = "aapl",
            # volume = 150,
            # direction = "long",
            # order_place_date = time.strftime('%Y-%m-%d %H:%M:%S'),
            # order_status = "test",
            # order_type = "market",
            # order_id=randrange(100000)
        )
        record.save()
        return record

    @staticmethod
    # update record status to expired
    def update(id):
        record = Signal.objects.get(id=id)
        #logging.debug("Code: uy8899. Record: " + str(record))
        record.status = "expired"
        record.save()
        return record



