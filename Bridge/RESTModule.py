import configparser
import requests

from Alert import Alert

class RESTModuleClass:
    def __init__(self, boxId:int, errorList: list[Alert]):
        self.boxId = boxId
        self.errorList = errorList
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')


    # request a tool by its uuid
    def requestByUUID(self, uuid: str):
        try:
            url = self.config.get('HTTP', 'URL', fallback='http://127.0.0.1/') + 'tools/by_uuid/' + uuid
            x = requests.get(url)
            return x.json()
        except:
            self.errorList.append(Alert('REST', 'Cannot communicate with REST server'))
            return None
        
    # request a list of all the tools in the box
    def requestToolList(self):
        try:
            url = self.config.get('HTTP', 'URL', fallback='http://127.0.0.1/') + 'boxes/' + str(self.boxId) + '/tool_list'
            x = requests.get(url)
            return x.json()
        except:
            self.errorList.append(Alert('REST', 'Cannot communicate with REST server'))
            return None
        

    # request thresholds of the box
    def requestThresholds(self):
        try:
            url = self.config.get('HTTP', 'URL', fallback='http://127.0.0.1/') + 'boxes/' + str(self.boxId) + '/thresholds'
            x = requests.get(url)
            return dict(x.json())
        except:
            self.errorList.append(Alert('REST', 'Cannot communicate with REST server'))
            return None
