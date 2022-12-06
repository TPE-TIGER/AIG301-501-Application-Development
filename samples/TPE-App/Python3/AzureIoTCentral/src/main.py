import time
from multiprocessing import Process, Queue
from tcp_program import tcp_server
from aic_program import aic_client

class main_program():
    def __init__(self):
        self.tcpProcessInQ = Queue()  
        self.tcpProcessOutQ = Queue()  
        self.aicProcessIQ = Queue() 
        self.aicProcessOutQ = Queue()   
        self.aic_status = ""
        self.connection_ts = ""
        self.aic_proc_running = False
    
    def run(self):
        tcp = tcp_server()
        tcp_proc = Process(target=tcp.run, args=(self.tcpProcessInQ, self.tcpProcessOutQ))
        tcp_proc.start()        
        
        while True:
            command = self.tcpProcessOutQ.get(block=True)
            if command == 'put exit':
                if self.aic_proc_running:
                    aic_proc.kill()
                break                                        # Exit whie loop
            
            if command == 'put start' :
                if not self.aic_proc_running:                
                    aic = aic_client()
                    aic_proc = Process(target=aic.run, args=(self.aicProcessIQ, self.aicProcessOutQ))
                    self.aic_status = "connecting "
                    self.connection_ts = str(time.time())
                    aic_proc.start()
                    try:
                        data = self.aicProcessOutQ.get(block=True, timeout=60000)
                        data = data.split("#")
                        self.aic_status = data[0]
                        self.connection_ts = data[1]
                        if self.aic_status.startswith('connected'):
                            self.aic_proc_running = True
                            continue                                
                    except:
                        print('reach except at line 39')
                         
                    print('[error] Azure IoT Central connection fail')
                    self.aic_status = "connection fail"
                    self.connection_ts = str(time.time())
                    aic_proc.kill()

            
            if command == 'get status':
                while not self.aicProcessOutQ.empty():
                    data = self.aicProcessOutQ.get(block=False)
                    data = data.split("#")
                    self.aic_status = data[0]
                    self.connection_ts = data[1]
                output = {}
                output['connectionStatus'] = self.aic_status
                output['connectionTS'] = self.connection_ts
                self.tcpProcessInQ.put(output, block=False)
            
            if command == 'put stop' :
                if self.aic_proc_running: 
                    self.aicProcessIQ.put('shutdown', block=False)      # Send shutdown command to aic program
                    self.aic_status = self.aicProcessOutQ.get(block=True, timeout=60000)
                    aic_proc.kill()                                                 # Waiting aic program close
                    self.aic_proc_running = False
        
        tcp_proc.join()                                                             # Waiting tcp program close


if __name__ == '__main__': 
    main = main_program()
    main.run()