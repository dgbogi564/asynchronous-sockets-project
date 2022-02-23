import socket
import errno
import select
import sys
import re


def rs(rs_hostname=None, rs_listenport=None, ts1_hostname=None, ts1_listenport=None, ts2_hostname=None, ts2_listenport=None):
    error = None

    if not rs_hostname:
        rs_hostname = socket.gethostbyname(socket.gethostname())
        rs_listenport = int(sys.argv[1])
        ts1_hostname = socket.gethostbyname(sys.argv[2])
        ts1_listenport = int(sys.argv[3])
        ts2_hostname = socket.gethostbyname(sys.argv[4])
        ts2_listenport = int(sys.argv[5])

    try:
        rss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        rss.bind((rs_hostname, rs_listenport))
        rss.settimeout(60)
        rss.listen(1)
        print("[RS]: RS server socket created")
        tss = [socket.socket(socket.AF_INET, socket.SOCK_STREAM), socket.socket(socket.AF_INET, socket.SOCK_STREAM)]
        tss[0].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tss[0].connect((ts1_hostname, ts1_listenport))
        tss[1].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tss[1].connect((ts2_hostname, ts2_listenport))
        print("[RS]: RS client sockets created")
    except socket.error as e:
        print("[RS]: Socket open error: {}".format(e))
        raise e

    print("[RS]: Server started at {}:{}".format(rs_hostname, rs_listenport))
    cs, addr = rss.accept()
    print("[RS]: Got a connection request from a client at {}".format(addr))

    while True:
        domain = ''
        query = ''
        try:
            query = recv([cs], 60)[0]
            if not query:
                break
            print("[RS]: Query received from client: {}".format(query))
            domain = re.findall('(?!^https\/\/)(?![www.])[a-zA-Z0-9]+.[^\/]+', query)[0]
            send(tss, domain, 5)
            print("[RS]: Query sent to TS servers: {}".format(query))
            while True:
                response, sock = recv(tss, 5)
                if domain in response:
                    break
            for i, s in enumerate(tss):
                if sock is s:
                    print("[RS]: Response received from TS{}: {}".format(i+1, response))
        except Exception as e:
            if isinstance(e, TimeoutError) and domain and domain in query:
                response = query + ' - TIMEOUT'
            else:
                print("[RS]: Exception occurred: {}".format(error))
                break

        try:
            send([cs], response, 10)
            print("[RS]: Response sent to client: {}".format(response))
        except Exception as e:
            if isinstance(e, TimeoutError):
                print("[RS]: Timeout occurred")
            else:
                print("[RS]: Exception occurred: {}".format(e))
            error = e
            break

    print("[RS]: Closing connection")
    rss.shutdown(socket.SHUT_RDWR)
    rss.close()
    for s in tss:
        s.shutdown(socket.SHUT_RDWR)
        s.close()
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
    rs()
