import json, time, os
from tpeHelper import tagHelper, apiHelper

class tagInstance():

    def __init__(self, provider, source, tag, value=None):
        self._provider = provider
        self._source = source
        self._tag = tag
        if value == None:
            self._value = 0
        else:
            self._value = value

class calculation():

    def __init__(self, value, scale, result):
        self._value = value
        self._scale = scale
        self._result = result

    def do_work(self):
        self._result._value = self._value._value * pow(10, self._scale._value)

config = {}
srcTags = {}
dstTags = {}
calculationList = []
myTagHelper = tagHelper()

def print_calc():
    global calculationList
    for calc in calculationList:
        print(calc._value._provider + '.' + calc._value._source + '.' + calc._value._tag + ': ' + str(calc._value._value))
        print(calc._scale._provider + '.' + calc._scale._source + '.' + calc._scale._tag + ': ' + str(calc._scale._value))
        print(calc._result._provider + '.' + calc._result._source + '.' + calc._result._tag + ': ' + str(calc._result._value))

def tag_callback(data, userdata):
#    print(time.strftime('%Y/%m/%d %H:%M:%S') + ' ' + str(userdata) + '; ' + data + '\n')
    global calculationList
    jsonData = json.loads(data)
    for tag in jsonData:
#        print(tag)
        for calc in calculationList:
            if calc._value._provider == tag['prvdName'] and calc._value._source == tag['srcName'] and calc._value._tag == tag['tagName']:
                calc._value._value = tag['dataValue']
            elif calc._scale._provider == tag['prvdName'] and calc._scale._source == tag['srcName'] and calc._scale._tag == tag['tagName']:
                calc._scale._value = tag['dataValue']
#    print('Before calculation:\n-----')
#    print_calc()
    
    for calc in calculationList:
        calc.do_work()
#    print('After calculation\n-----')
    print_calc()

    global myTagHelper
    for calc in calculationList:
        myTagHelper.set_tag_value(calc._result._provider, calc._result._source, calc._result._tag, 'double', calc._result._value)

def load_config():
    global config
    global srcTags
    global dstTags
    if (os.path.isfile('config.json') is True):
        with open('config.json') as f:
            config = json.load(f)
    for item in config:
        myCalculation = calculation(None, None, None)
        for tagType in item['src']:
#            print('Type: ' + tagType)
            for provider in item['src'][tagType]:
#                print('Provider: ' + provider)
                if provider not in srcTags:
                    srcTags[provider] = {}
                for source in item['src'][tagType][provider]:
#                    print('Source: ' + source)
                    if source not in srcTags[provider]:
                        srcTags[provider][source] = []
                    for tag in item['src'][tagType][provider][source]:
 #                       print('Tag: ' + tag)
                        srcTags[provider][source].append(tag)
                        myTagInstance = tagInstance(provider, source, tag)
                        if tagType == 'value':
                            myCalculation._value = myTagInstance
                        elif tagType == 'scale':
                            myCalculation._scale = myTagInstance
        for provider in item['dst']:
            if provider not in dstTags:
                dstTags[provider] = {}
            for source in item['dst'][provider]:
                if source not in dstTags[provider]:
                    dstTags[provider][source] = []
                dstTags[provider][source].append(item['dst'][provider][source])
                myTagInstance = tagInstance(provider, source, item['dst'][provider][source], 0)
                myCalculation._result = myTagInstance
        calculationList.append(myCalculation)

#    print(srcTags)
#    print(dstTags)
#    print_calc()

if __name__ == '__main__':
    myTagHelper.set_callback(tag_callback)

    load_config()

    # Create virtual tags
    myApiHelper = apiHelper()
    payload = {}
    for provider in dstTags:
        payload['prvdName'] = provider
        for source in dstTags[provider]:
            payload['srcName'] = source
            for tag in dstTags[provider][source]:
                payload['tagName'] = tag
                payload['dataType'] = 'double'
                payload['dataUnit'] = ''
                payload['access'] = 'rw'
#                print(payload)
                result = myApiHelper.invoke_api('post', '/tags/virtual', payload)
                if result['status'] >= 300:
                    print('Failed to create virtual tags: ' + provider + '.' + source + '.' + tag)
                    print(result)

    myTagHelper.set_tags(srcTags)
#     myTagHelper.start_stream

    while True:
        myTagHelper.get_tag_values()
        time.sleep(5)
