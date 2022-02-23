import select
import socket
import errno


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
