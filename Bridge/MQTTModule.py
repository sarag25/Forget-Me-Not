import configparser
import paho.mqtt.client as mqtt
from typing import Callable
import re
import json
from Alert import Alert

def selectObjIDInObjectURLs(objId: int, objectURLs : list[dict['id': int, 'URL': int]]):
    for entry in objectURLs:
        if entry['id'] == objId:
            return entry
        
    return None


class MQTTModuleClass:
    def __init__(self, boxId, errorList: list[Alert], onObjMove : Callable[[str], None], objIdList: list[int]):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.clientMQTT = mqtt.Client()
        self.boxId = boxId
        self.errorList = errorList
        self.onObjMove = onObjMove

        boxesURL = self.config.get('MQTT', 'PubTopicBox', fallback= 'boxes')

        self.pubBoxGPS = boxesURL + str(self.boxId) + self.config.get('MQTT', 'PubTopicGPS', fallback='/GPS')
        
        self.pubBoxSerie = boxesURL + str(self.boxId) + self.config.get('MQTT', 'PubTopicBoxSerie', fallback='/serie')
        
        self.pubBoxUser = boxesURL + str(self.boxId) + self.config.get('MQTT', 'PubTopicUser', fallback='/user')

        self.objectURLs = []
        for objId in objIdList:
            self.objectURLs.append({ 
                'id': objId,
                'URL': self.config.get('MQTT', 'TopicObj', fallback='/objects/') + str(objId) + self.config.get('MQTT', 'TopicObjBox', fallback='/box')
            })
        self.objectURLRegex = r'^' + self.config.get('MQTT', 'TopicObj', fallback='/objects/') + r'(\d+)' + self.config.get('MQTT', 'TopicObjBox', fallback='/box') + r'$'

        self.clientMQTT.on_connect = self.on_connect
        self.clientMQTT.on_message = self.on_message

        try:
            self.clientMQTT.connect(
                self.config.get("MQTT","Server", fallback= "localhost"),
                self.config.getint("MQTT", "Port", fallback= 1883), 60)
            self.clientMQTT.loop_start()

            for url in self.objectURLs:
                self.clientMQTT.publish(url['URL'], self.boxId)
            alert = Alert('MQTT', 'Connected to MQTT broker')
            self.errorList.append(alert)
        except ConnectionRefusedError:
            print('mosquitto server is down')
            alert = Alert('MQTT', 'Cannot connect to MQTT broker')
            self.errorList.append(alert)
        

    def on_connect(self, client, userdata, flags, rc):
        for subscribe in self.objectURLs:
            self.clientMQTT.subscribe(subscribe['URL'])

        # Only for debug purposes
        # self.clientMQTT.subscribe(self.pubBoxGPS['longitude'])
        # self.clientMQTT.subscribe(self.pubBoxGPS['latitude'])

    
    # when an object is put into a box and (maybe) removed from another one
    def on_message(self, client, userdata, msg: mqtt.MQTTMessage):
        match_obj = re.search(self.objectURLRegex, msg.topic)
        if match_obj is not None:  # WARNING: verify
            objId = int(match_obj.group(1))
            newBox = int(msg.payload)
            if newBox != self.boxId:
                entry = selectObjIDInObjectURLs(objId, self.objectURLs)
                if entry is not None:
                    self.objectURLs.remove(entry)
                    self.clientMQTT.unsubscribe(entry['URL'])
                    self.onObjMove(objId)
                    print('Obj ' + str(objId) + ' has been removed from box ' + str(self.boxId))

    
    # add an object
    def publish_obj(self, objId):
        # linked
        url = { 
            'id': objId,
            'URL': self.config.get('MQTT', 'TopicObj', fallback='/objects/') + str(objId) + self.config.get('MQTT', 'TopicObjBox', fallback='/box')
        }
        self.objectURLs.append(url)
        pub = self.clientMQTT.publish(url['URL'], self.boxId)
        try:
            pub.is_published()
        except RuntimeError:
             self.errorList.append(Alert('MQTT', 'MQTT broker has accidentally disconnected'))
        self.clientMQTT.subscribe(url['URL'])
        

    def publish_box_position(self, position_long: float, position_lat: float):
        # to link
        pub = self.clientMQTT.publish(self.pubBoxGPS, json.dumps({
            'longitude': position_long,
            'latitude': position_lat
        }))
        
        try:
            pub.is_published()
        except RuntimeError:
             self.errorList.append(Alert('MQTT', 'MQTT broker has accidentally disconnected'))


    def publish_box_user(self, userId):
        # linked
        pub = self.clientMQTT.publish(self.pubBoxUser, userId)
        try:
            pub.is_published()
        except RuntimeError:
             self.errorList.append(Alert('MQTT', 'MQTT broker has accidentally disconnected'))


    def publish_box_serie(self, error, temperature, humidity, acceleration, weight):
        # linked
        pub = self.clientMQTT.publish(self.pubBoxSerie, json.dumps({
                'error': error,
                'temperature': temperature,
                'humidity': humidity,
                'acceleration': acceleration,
                'weight': weight,
            })
        )

        try:
            pub.is_published()
        except RuntimeError:
             self.errorList.append(Alert('MQTT', 'MQTT broker has accidentally disconnected'))
