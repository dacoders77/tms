# Apps aren't loaded error
# https://www.reddit.com/r/djangolearning/comments/c41m6n/problem_running_management_commands_in_a_py_in/
import django, time
django.setup()
from django.core.management.base import BaseCommand, CommandError
from multiprocessing import Process

import threading


import sys
sys.path.insert(1, 'classes/trade/') # Path to Trading app
from Trading import TestApp
from Trading import Trading


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('d.py Method: handle')

        app = TestApp()
        app.connect("127.0.0.1", 4002, 0)
        print("serverVersion:%s connectionTime:%s" % (app.serverVersion(), app.twsConnectionTime()))

        thread = MyThread(1, app)
        thread.start()
        thread = MyThread(4, app)
        thread.start()



# Thread class. Use: import threading
class MyThread(threading.Thread):
    # Constructor. We pass app class instance as an argument
    def __init__(self, number, app):
        super(MyThread, self).__init__()
        self.number = number
        self.app = app
    # Run method
    def run(self):
        for i in range(10):
            print(f"fare: {i} self num: {self.number} ib: {self.app}")
            time.sleep(self.number)


def fare():
    for i in range(10):
        print(f"fare: {i}")
        time.sleep(4)


def bare():
    for i in range(10):
        print(f"bare: {i}")
        time.sleep(1)


def class1():
    app = TestApp()
    app.main()


def class2():
    testApp = TestApp()
    testApp.dbCheck()








