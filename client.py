import errno
import socket
import select
import sys


def client(rs_hostname=None, rs_listenport=None):
    error = None

    if not rs_hostname:
        rs_hostname = sys.argv[1]
        rs_listenport = int(sys.argv[2])

    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        cs.connect((rs_hostname, rs_listenport))
        cs.setblocking(False)
        print("[C]: Client socket created")
    except socket.error as e:
        print("Socket open error: {}".format(e))
        raise e

    with open('PROJ2-HNS.txt', 'r') as requests, open('RESOLVED.txt', 'w+') as resolved:
        for query in requests:
            query = query.rstrip()
            try:
                send([cs], query, 5)
                print("\n[C]: Query sent to root server: {}".format(query))

                response = recv([cs], 20)[0]
                if not response:
                    break
                print("[C]: Response received from root server: {}".format(response))
                resolved.write(response + '\n')
            except Exception as e:
                if e is TimeoutError:
                    print("[C]: Timeout occurred")
                else:
                    print("[C]: Exception occurred: {}".format(e))
                error = e
                break

    print("\n[C]: Closing connection")
    cs.shutdown(socket.SHUT_RDWR)
    cs.close()
    if error:
        raise error
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
    client()
