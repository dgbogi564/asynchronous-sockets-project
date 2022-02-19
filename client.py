import errno
import socket
import select
import sys


def client():
    error = None

    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("[C]: Client socket created")
    except socket.error as e:
        print('Socket open error: {} \n'.format(e))
        raise e

    port = 50007
    localhost_addr = socket.gethostbyname(socket.gethostname())
    server_binding = (localhost_addr, port)
    cs.connect(server_binding)
    cs.setblocking(False)

    with open("PROJ2-HNS.txt", "r") as file:
        for request in file.read().split('\n'):
            request = request.encode("utf-8")
            print("[C]: Sending query: {}".format(request))
            sent = 0
            while len(request):
                try:
                    sent += cs.send(request[sent:])
                except socket.error as e:
                    if e.errno != errno.EAGAIN:
                        error = e
                        break
                select.select([], [cs], [])

            msg = ''
            ready = select.select([], [cs], [], 5)
            while ready[0]:
                try:
                    buf = cs.recv(100)
                    if not buf:
                        break
                    msg += buf
                except socket.error as e:
                    if e.errno != errno.EAGAIN:
                        error = e
                        break
                    ready = select.select([], [cs], [], 5)
            if ready[0]:
                print("[C]: Data received from root server: \n{}".format(msg))
            else:
                print"[C]: Timeout occurred"

    print("[C]: Closing connection")
    cs.shutdown(socket.SHUT_RDWR)
    cs.close()

    if error:
        print("[C]: Exception occurred")
        raise e
    exit()
