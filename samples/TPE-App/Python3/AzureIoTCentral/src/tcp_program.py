import socket, json

class tcp_server():
    def __init__(self, port=10000):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('0.0.0.0', port)        
    
    def run(self, tcpProcessInQ, tcpProcessOutQ):
        print('[info] tcp socket starting on {} port {}'.format(*self.server_address)) 
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      
        self.sock.bind(self.server_address)   
        self.sock.listen(1) 
        
        self.handle_received_command(tcpProcessInQ, tcpProcessOutQ)
    
    def handle_received_command(self, tcpProcessInQ, tcpProcessOutQ):
        shutdown = False
        command = None
        while True:
            # Wait for a connection
            print('[info] waiting for a tcp connection')
            connection, client_address = self.sock.accept()

            try:
                print('[info] tcp connection from ', client_address)
                while True:
                    # Receive client data hardcode Max 128 bytes
                    command = connection.recv(128).decode("utf-8")
                    command = command.replace('\r\n', '')
                    print('[info] command: ' + command)                    
                    if command == 'put start':        
                        tcpProcessOutQ.put(command, block=False)                
                        connection.sendall(b'OK')  
                        break
                    elif command == 'put stop':
                        tcpProcessOutQ.put(command, block=False)
                        connection.sendall(b'OK')  
                        break
                    elif command == 'get status':
                        tcpProcessOutQ.put(command, block=False)
                        try:
                            data = tcpProcessInQ.get(block=True, timeout=7000)
                            dataString = json.dumps(data)
                            connection.sendall(dataString.encode()) 
                        except:
                            connection.sendall("......".encode())                        
                        break
                    elif command == 'put exit':
                        shutdown = True
                        tcpProcessOutQ.put(command, block=False)
                        connection.sendall(b'OK')
                        break
                    else:
                        connection.sendall(b'Invalid Command')
                        break
            finally:
                # Clean up the connection                
                print('[info] tcp connection closed')
                connection.close()
            
            # Receive command to start connection, and now is stop
            if shutdown:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                return