import errno
import socket
import select
import sys
import re


def ts1(ts1_hostname=None, ts1_listenport=None):
    error = None

    if not ts1_hostname:
        ts1_hostname = socket.gethostbyname(socket.gethostname())
        ts1_listenport = int(sys.argv[1])
    try:
        ts1s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts1s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ts1s.bind((ts1_hostname, ts1_listenport))
        ts1s.settimeout(60)
        ts1s.listen(1)
        print("[TS1]: TS1 socket created")
    except socket.error as e:
        print("[TS1]: Socket open error: {}".format(e))
        raise e

    print("[TS1]: Server started at {}:{}".format(ts1_hostname, ts1_listenport))
    rs, addr = ts1s.accept()
    print("[TS1]: Got a connection request from the root server at {}".format(addr))

    with open('PROJ2-DNSTS1.txt', 'r') as table:
        while True:
            try:
                query = recv([rs], 60)[0]
                if not query:
                    break
                print("[TS1]: Query received from root server: {}".format(query))
                table.seek(0)
                for line in table.readlines():
                    if query in line:
                        send([rs], line.strip() + ' IN', 5)
                        print("[TS1]: Response sent to root server: {}".format(line))
                        break
            except Exception as e:
                if isinstance(e, TimeoutError):
                    print("[TS1]: Timeout occurred")
                else:
                    print("[TS1]: Exception occurred: {}".format(e))
                error = e
                break

    print("[TS1]: Closing connection")
    ts1s.shutdown(socket.SHUT_RDWR)
    ts1s.close()
    if error:
        raise
    exit()


class TimeoutError(IOError):
    def __init__(self):
        self.errno = errno.ETIMEDOUT
        self.message = 'Timeout occurred'

    def __str__(self):
        return self.message


def send(sockets, data, timeout):
    data += '\0'
    for sock in sockets:
        sent = 0
        while len(data[sent:]):
            try:
                sent += sock.send(data[sent:])
            except socket.error as e:
                if e.errno != errno.EAGAIN:
                    raise e
                if not select.select([], [sock], [], timeout)[1]:
                    raise TimeoutError()


def recv(sockets, timeout):

    # check if timeout occurred
    ready = select.select(sockets, [], [], timeout)[0]
    if not ready:
        raise TimeoutError()

    # receive data
    sock = ready[0]
    data = ''
    while True:
        try:
            buf = sock.recv(100)
            data += buf if buf else ''
            if not buf or '\0' in buf:
                data = data.rstrip('\0').strip()
                break
        except socket.error as e:
            if e.errno != errno.EAGAIN:
                raise e
            select.select([sock], [], [], timeout)
    return data, sock


if __name__ == "__main__":
    ts1()
