import socket
import errno
import select
import sys

def rs():
    try:
        rs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[RS]: RS socket created')
        ts1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[RS]: TS1 socket created')
        ts2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[RS]: TS2 socket created')
    except socket.error as e:
        print('Socket open error: {}\n'.format(e))
        exit()

    #recive port and names from command line
    rs_port = int(sys.argv[1])
    ts1_name = str(sys.argv[2])
    ts1_port = int(sys.argv[3])
    ts2_name = str(sys.argv[4])
    ts2_port = int(sys.argv[5])
                   
    #bind servers              
    rs_binding = ('', rs_port)
    ts1_binding = (ts1_name, ts1_port)
    ts2_binding = (ts2_name, ts2_port)

    rs_socket.bind(rs_binding)
    rs_socket.listen(5)
    #rs_socket.setblocking(False)
    ts1.connect(ts1_binding)
    #ts1.setblocking(False)
    ts2.connect(ts2_binding)
    #ts2.setblocking(False)

    hostname = socket.gethostname()

    print('[RS]: Hostname: {} IP: {}'.format(hostname, socket.gethostbyname(hostname)))

    #TS server list for select
    sockets = [ts1, ts2]

    #accept connection from client
    cs, addr = rs_socket.accept()
    print('[RS]: Got a connection request from a client at {}'.format(addr))

    while True:
        #receive queries from client
        data_from_client = cs.recv(100)
        query = data_from_client.decode('utf-8')
        print("[RS]: Query received from client: {}".format(query))

        #send queries to TS servers 
        ts1.send(data_from_client)
        ts2.send(data_from_client)
        
        #determine which sockets can be read from
        readable_sockets, _, _ = select.select(sockets, [], [], 5)

        #check if either TS server can be read from
        if readable_sockets:
            for s in readable_sockets:
                data = s.recv(100)
                msg = data.decode('utf-8')
                if s is ts1:
                    print('[RS]: Response received from TS1 server: {}'.format(msg))
                else:
                    print('[RS]: Response received from TS2 server: {}'.format(msg))

                #send response to client
                cs.send(data)
        #timeout        
        else:
              print('[RS]: Timeout occurred')

              #send response to client
              msg = '{} - TIMED OUT'.format(query)
              cs.send(msg.encode('utf-8'))
    
    #close sockets
    rs_socket.close()
    ts1.close()
    ts2.close()
    exit() 

if __name__ == "__main__":
    rs()
    
