import errno
import socket
import select
import sys

def getTable(f):
    table = {}
    for l in f.read().split('\n'):
        words = l.split(" ")
        name = words[0].lower() #key is lowercase for case-insensitive lookup
        table[name] = l
    return table

def ts1():
    try:
        ts1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[TS1]: TS1 socket created')
    except socket.err as e:
        print('Socket open error: {}\n'.format(e))
        exit()

    #receive port from command line
    port = int(sys.argv[1])
    binding = ('', port)
    ts1_socket.bind(binding)
    ts1_socket.listen(5)

    hostname = socket.gethostname()
    host_addr = socket.gethostbyname(hostname)

    print('[TS1]: Hostname: {} IP: {}'.format(hostname, host_addr))
          
    #open dns file
    with open('PROJ2-DNSTS1.txt', 'r') as f:
        #get dns table
        dns = getTable(f)
    f.close()

    #accept connection from rs
    rs, addr = ts1_socket.accept()
    print('[TS1]: Got a connection request from RS at {}'.format(addr))
    
    while True:
        #recieve queries from rs
        data_from_rs = rs.recv(100)
        query = data_from_rs.decode('utf-8')
        print('[TS1]: Query received from RS: {}'.format(query))

        #check if query is in dns
        if data_from_rs.lower() in dns:
            msg = dns.get(query) + ' IN'
            #send message to rs
            rs.send(msg)
            print('[TS1]: Query found in DNS Table')

    ts1_socket.close()
    rs.close()
    exit()

if __name__ == "__main__":
    ts1()
