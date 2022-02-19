import threading
import time
import random

from client import client
from rs import rs
from ts1 import ts1
from ts2 import ts2

if __name__ == "__main__":
    t1 = threading.Thread(name='dns1', target=ts1)
    t1.start()

    t2 = threading.Thread(name='dns2', target=ts2)
    t2.start()

    time.sleep(random.random() * 5)
    t3 = threading.Thread(name='root server', target=rs)
    t3.start()

    time.sleep(random.random() * 5)
    client()
    print("Done.")
