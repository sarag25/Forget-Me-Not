import time
from turtle import position
from serial import SerialException
from MQTTModule import MQTTModuleClass
from CommunicationModule import CommunicationModuleClass
from Alert import Alert
from RESTModule import RESTModuleClass
from cmath import pi

class Tool:
    def __init__(self, id: int, uuid: str, name: str, status: bool, latitude_last_position: float = None, longitude_last_position: float = None):
        self.id = id
        self.uuid = uuid
        self.name = name
        self.status = status
        self.latitude_last_position = latitude_last_position
        self.longitude_last_position = longitude_last_position

    def toDict(self):
        return {'ToolString': self.name, 'Status': self.status}
    
    def toDictLostTool(self):
        return {
            'Name': self.name,
            'Lat': self.latitude_last_position,
            'Long': self.longitude_last_position
        }

def byUUID(toolList: list[Tool], uuid: str) -> Tool:
    for i in toolList:
        if i.uuid == uuid:
            return i
    
    return None

class Box:
    def __init__(self):
        self.boxId = -1
        self.errorList: list[Alert] = []
        self.toolList: list[Tool] = []
        self.mqtt: MQTTModuleClass = None
        self.cm = CommunicationModuleClass(self.onObject, self.onAlertWeight, self.onAlertBump, self.onAlertHum, self.onAlertTemp, self.onStatusReceived, self.onIdReceived)
        self.weight_threshold = 0
        self.acceleration_threshold = 0
        self.temperature_min = 0
        self.temperature_max = 0
        self.humidity_threshold = 0
        self.tare = 0
        self.rest: RESTModuleClass = None
        self.lostToolsList: list[Tool] = []



    def onObject(self,uuid):
        found = byUUID(self.toolList, uuid)

        if found == None:
            # oggetto non trovato
            resp = self.rest.requestByUUID(uuid)
            if resp is not None:
                self.toolList.append( Tool(resp['id'], resp['UUID'], resp['name'], True) )

                if self.mqtt is not None:
                    self.mqtt.publish_obj(resp['id'])
        else:
            found.status = not found.status

    def onAlertWeight(self, weigth: int):
        self.errorList.append(Alert('ERRORE PESO', 'Il peso registrato è ' + str(weigth/1000.0) + ' kg'))

    def onAlertBump(self):
        self.errorList.append(Alert('ERRORE URTO', 'Urto rilevato'))

    def onAlertHum(self):
        self.errorList.append(Alert('ERRORE UMIDITÀ', 'Umidità eccessiva'))

    def onAlertTemp(self, temp: int):
        self.errorList.append(Alert('ERRORE TEMPERATURA', 'Temperatura registrata: ' + str(temp) + ' °'))

    def onIdReceived(self, id: int):
        self.boxId = id

    def onStatusReceived(self, error: bool, temperature: int, humidity: int, acceleration: int, weight: int):
        if self.mqtt is not None:
            self.mqtt.publish_box_serie(error, temperature, humidity, acceleration, weight)

    def getErrorList(self) -> list[dict['ErrorType': str, 'ErrorString': str]]:
        returnList = []
        for error in self.errorList:
            returnList.append(error.toDict())
        return returnList


    def getToolsList(self) -> list[dict['ToolString': str, 'Status': bool]]:
        returnList = []
        for tool in self.toolList:
            returnList.append(tool.toDict())
        return returnList


    def findMe(self):
        self.cm.sendFindMe()


    def stopFindMe(self):
        self.cm.sendStopFindMe()

    
    def onObjMove(self, idTool):
        for tool in self.toolList:
            if tool.id == idTool:
                self.toolList.remove(tool)
                if tool in self.lostToolsList:
                    self.lostToolsList.remove(tool)
                return


    def connect(self, portname: str) -> dict['ID': str, 'Status': bool]:
        self.cm.portname = portname
        if self.cm.connect() is False:
            return {'ID': self.boxId, 'Status': False}
        
        self.cm.askBoxId()

        while self.boxId == -1:
            self.cm.readPacket()
        
        self.rest = RESTModuleClass(self.boxId, self.errorList)

        resp = self.rest.requestToolList()

        objIdList = []
        self.toolList = []
        for tool in resp:
            self.toolList.append(Tool(tool['id'], tool['uuid'], tool['name'], True))
            objIdList.append(tool['id'])

        self.mqtt = MQTTModuleClass(self.boxId, self.errorList, self.onObjMove, objIdList)
        
        resp = self.rest.requestThresholds()

        self.weight_threshold = int(resp.get('weight_threshold', 0))
        self.acceleration_threshold = int(resp.get('acceleration_threshold', 0))
        self.temperature_min = int(resp.get('temperature_min', 0))
        self.temperature_max = int(resp.get('temperature_max', 0))
        self.humidity_threshold = int(resp.get('humidity_threshold', 0))
        self.tare = int(resp.get('tare', 0))

        self.cm.sendWeightThreshold(self.weight_threshold)
        self.cm.sendBumpThreshold(self.acceleration_threshold)
        self.cm.sendTemperatureThreshold(self.temperature_min, self.temperature_max)
        self.cm.sendHumidityThreshold(self.humidity_threshold)
        self.cm.sendTare(self.tare)

        return {'ID': self.boxId, 'Status': True}
        

    def disconnect(self) -> dict['ID': str, 'Status': bool]:
        self.cm.disconnect()
        return {'ID': self.boxId, 'Status': False}


    def update(self) -> tuple[
        dict['ID': str, 'Status': bool], 
        list[dict['ToolString': str, 'Status': bool]], 
        list[dict['ErrorType': str, 'ErrorString': str]]
    ]:
        try:  
            if self.cm.ser is not None:
                self.cm.readPacket()
            else:
                return {'ID': self.boxId, 'Status': False}, self.getToolsList(), self.getErrorList()
        except SerialException:
            return {'ID': self.boxId, 'Status': False}, self.getToolsList(), self.getErrorList()
        
        return {'ID': self.boxId, 'Status': True}, self.getToolsList(), self.getErrorList()


    def bindOperator(self, operator_id: int):
        if self.mqtt is not None:
            self.mqtt.publish_box_user(operator_id)

    def getPositionAndLostObjectsPositions(self, index: int = 0) -> tuple[dict['Lat': float, 'Long': float], list[dict['Name': str, 'Lat': float, 'Long': float]]]:
        positionList = [{
            'Long': 41.90382, 
            'Lat': 12.44690,
        },
        {
            'Long': 41.90383, 
            'Lat': 12.44690,
        },
        {
            'Long': 44.65026,
            'Lat': 10.83933
        },
        {
            'Long': 44.88051,
            'Lat': 10.91188,
        },
        ]
        index = index % len(positionList)

        position = positionList[index]
        if self.mqtt is not None:
            self.mqtt.publish_box_position(position['Lat'], position['Long'])

        outTools: list[Tool] = []

        for tool in self.toolList:
            if tool.status == False:
                outTools.append(tool)
            else:
                if tool in self.lostToolsList:
                    self.lostToolsList.remove(tool)
                tool.latitude_last_position = position['Lat']
                tool.longitude_last_position = position['Long']

        for outTool in outTools:
            if abs((outTool.longitude_last_position - position['Long'])**2 +
                   (outTool.latitude_last_position - position['Lat'])**2) > 0.001**2:
                if outTool not in self.lostToolsList:
                    self.lostToolsList.append(outTool)
                self.errorList.append(Alert(errorType='TOOLS LOST', errorString='Some tools have been lost, check the map...'))
        
        returnLostToolsDict = []
        for lostTool in self.lostToolsList:
            returnLostToolsDict.append(lostTool.toDictLostTool())

        return positionList[index], returnLostToolsDict
    

    def getThreshold(self) -> dict['WeightThreshold': int, 'AccelerationThreshold': int, 'TemperatureMin': int, 'TemperatureMax': int, 'HumidityThreshold': int]:
        return {
            'WeightThreshold': self.weight_threshold, 
            'AccelerationThreshold': self.acceleration_threshold, 
            'TemperatureMin': self.temperature_min, 
            'TemperatureMax': self.temperature_max, 
            'HumidityThreshold': self.humidity_threshold
        }
        