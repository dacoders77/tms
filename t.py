import os
from multiprocessing import Process
import time

# String with variables in it
# number = 2
# print(f"The number {number}")


def square(number):
    result = number * number
    print(f"number={number}. result={result}")


def fare():
    for i in range(10):
        print(f"fare:{i}")
        time.sleep(1.2)


def bare():
    for i in range(10):
        print(f"bare: {i}")
        time.sleep(2)


if __name__ == '__main__':
    # process = Process(target=square, args=(6,))
    # process.start()

    process = Process(target=fare)
    process.start()

    process = Process(target=bare)
    process.start()