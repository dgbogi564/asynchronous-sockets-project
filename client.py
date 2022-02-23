import errno
import socket
import select
import sys
from sock_helper import TimeoutError, send, recv


def client(rs_hostname=None, rs_listenport=None):
    error = None

    if not rs_hostname:
        rs_hostname = sys.argv[0]
        rs_listenport = int(sys.argv[1])

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


if __name__ == "__main__":
    client()
