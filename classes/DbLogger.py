import logging
import time
from ib.models import Log
from pprint import pprint


# Customized logging handler that puts logs to the database
class DbLogger(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        # Add record to DB
        r = Log()
        r.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        r.level_name = record.levelname
        r.level = record.lineno
        r.source = record.filename
        r.message = record.message
        try:
            r.save()
        except:
            print('DbLogger.py update model exception catch. Code: 6677hh')


