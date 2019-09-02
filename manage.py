#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import time
from multiprocessing import Process

def fare():
    for i in range(10):
        print(f"fare:{i}")
        time.sleep(1.2)


def bare():
    for i in range(10):
        print(f"bare: {i}")
        time.sleep(2)

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
