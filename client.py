import errno
import socket
import select
import sys


def client():
    error = None

    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[C]: Client socket created")
    except socket.error as e:
        print('Socket open error: {} \n'.format(e))
        exit()

    #receive hostname and port from command line
    name = str(sys.argv[1])
    port = int(sys.argv[2])
    server_binding = (name, port)
    cs.connect(server_binding)

    #print hostname and IP of machine
    hostname = socket.gethostname()
    host_addr = socket.gethostbyname(hostname)
    print('[C]: Hostname: {} IP: {}'.format(hostname, host_addr))

    resolved_file = open('RESOLVED.txt', 'w')
    
    with open("PROJ2-HNS.txt", "r") as file:
        for request in file.read().split('\n'):
            query = request.encode("utf-8")
            print("[C]: Sending query: {}".format(request))
            cs.send(query)

            #determine if rs can be read from
            readable, _, _ = select.select([cs], [], [], 10)

            if readable:
                data = cs.recv(100)
                msg = data.decode('utf-8')
                print('[C]: Data received from root server: {}'.format(msg))
                resolved_file.write(msg + '\n')
            else:
                print('[C]: Timeout occurred')         

    print("[C]: Closing connection")
    cs.close()

    if error:
        print("[C]: Exception occurred")
        raise error
    exit()

if __name__ == "__main__":
    client()
