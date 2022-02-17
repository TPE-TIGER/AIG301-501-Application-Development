import time, requests
from thingspro.edge.tag_v1 import tag


class backendProcess():
    def __init__(self):
        self.subscriber = tag.Subscriber()
        self.publisher = tag.Publisher()
        self.webAPIURL = 'http://127.0.0.1/api/v1'
        self.headers = {}
        self.headers["Content-Type"] = 'application/json'
        
    def waitWebAPI(self):
         # Invoke this application's self Restful API till ready
        while True:
            cmdURL = self.webAPIURL + '/hello-world'
            try:
                response = requests.get(cmdURL, json=None, headers=self.headers, verify=False)
                if response.text == 'Hello World.':
                    print('API Ready')
                    return
                else:
                    print('Waiting API')
                    time.sleep(10)
            except:
                print('Waiting API')
                time.sleep(10)
            
        
    def createTag(self, prvdName, srcName, tagName, dataType):
        # Invoke this application's self Restful API to create Tag
        cmdURL = self.webAPIURL + '/hello-world/tag'
        postTag = {
            'prvdName': prvdName,
            'srcName': srcName,
            'tagName': tagName,            
            'dataType': dataType,
            'access': 'rw'
        }         
        response = requests.post(cmdURL, json=postTag, headers=self.headers, verify=False)
        print(response.status_code)
        print(response.text)
    
    def C_to_F(self, inputC):
        F = ((inputC*9) / 5) + 32
        return F
    
    def tagDataCallback(self, data={}):
        timestamp=int(time.time()*1000000)  
        if data["tagName"] == 'tag02':
            F = self.C_to_F(data['dataValue'])
            tag03 = {
                    'prvdName': 'virtual',
                    'srcName': 'hello-world',
                    'tagName': 'tag03',            
                    'dataValue': int(F),
                    'dataType': 'int32',
                    'ts': timestamp        
                }  
            self.publisher.publish(tag03)
            
            if (F >= 100):     
                tag01Value = 'Over Heat'
            else:
                tag01Value = 'Normal'                     
            tag01 = {
                'prvdName': 'virtual',
                'srcName': 'hello-world',
                'tagName': 'tag01',            
                'dataValue': tag01Value,
                'dataType': 'string',
                'ts': timestamp        
            }             
            self.publisher.publish(tag01)            
    
    def start(self):
        # Waiting Web API
        self.waitWebAPI()
        
        # Create virtual tags before subscribe them
        self.createTag('virtual', 'hello-world', 'tag01', 'string')
        self.createTag('virtual', 'hello-world', 'tag02', 'int32')
        self.createTag('virtual', 'hello-world', 'tag03', 'int32')        
        
        # Subscribe virtual tags, and declare call back function        
        self.subscriber.subscribe_callback(self.tagDataCallback)        
        self.subscriber.subscribe('virtual', 'hello-world', ['tag01', 'tag02'])
        
        while True:
            time.sleep(1)

if __name__ == '__main__':  
    # Launch Azure IoT Central Client
    bgprocess = backendProcess()
    bgprocess.start()
