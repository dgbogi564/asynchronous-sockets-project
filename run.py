import threading
import time
import random
import socket

from client import client
from rs import rs
from ts1 import ts1
from ts2 import ts2
import socket


def get_open_port(hosts):
    ports = []
    for host in hosts:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, 0))
        ports.append(s.getsockname()[1])
    return ports


if __name__ == "__main__":
    rs_hostname = socket.gethostbyname(socket.gethostname()) #"ilab4.cs.rutgers.edu"
    ts1_hostname = socket.gethostbyname(socket.gethostname()) #"ilab2.cs.rutgers.edu"
    ts2_hostname = socket.gethostbyname(socket.gethostname()) #"ilab3.cs.rutgers.edu"
    port = get_open_port([rs_hostname, ts1_hostname, ts2_hostname])
    rs_listenport = port[0]
    ts1_listenport = port[1]
    ts2_listenport = port[2]

    t1 = threading.Thread(name='dns1', target=ts1, args=[ts1_hostname, ts1_listenport])
    t1.start()

    t2 = threading.Thread(name='dns2', target=ts2, args=[ts2_hostname, ts2_listenport])
    t2.start()

    time.sleep(random.random() * 5)
    t3 = threading.Thread(name='root server', target=rs,
                          args=[rs_hostname, rs_listenport, ts1_hostname, ts1_listenport, ts2_hostname, ts2_listenport])
    t3.start()

    time.sleep(random.random() * 5)
    client(rs_hostname, rs_listenport)
    print("Done.")
