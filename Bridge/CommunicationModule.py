from email import message
from enum import Enum
from typing import Callable
import serial
import time
import requests
import configparser

from MQTTModule import MQTTModuleClass


class MsgType(Enum):
    NOT_VALID = 0  # A message having this code should be discarded

    # SEND MESSAGES
    WEIGHT = 1
    BUMP = 2
    TEMP = 3
    HUM = 4

    # ALERT MESSAGES 
    ALERT_WEIGHT = 5
    ALERT_BUMP = 6
    ALERT_TEMP = 7
    ALERT_HUM = 8

    # OBJECT IN/OUT 
    OBJ = 9

    # MAKE AND STOP SOUND 
    FIND_ME = 10
    STOP_FIND_ME = 11

    # STATUS
    STATUS = 12

    # TARE
    TARE = 13

    ID_REQUEST = 14
    ID_ANSWER = 15


class Msg:
    def __init__(self, ser: serial.Serial, type: MsgType, length: int, content: bytes):
        self.ser = ser
        self.type = type
        self.length = length
        self.content = content
    

    def send(self):
        if self.ser is not None:
            packet = b''
            packet += b'\xfe'
            packet += int(self.length).to_bytes(length=1, byteorder='little')
            packet += int(self.type.value).to_bytes(length=1, byteorder='little')
            if (self.length > 0):
                packet += self.content
            packet += b'\xff'
            self.ser.write(packet)
        else:
            print('ERROR: cannot send messages, no serial communication')


    def read(ser: serial.Serial):
        restore_timeout = ser.timeout

        ser.timeout = 0
        firstByte = ser.read()
        if firstByte != b'\xfe':
            ser.timeout = restore_timeout
            return None
        
        ser.timeout = 1
        header = ser.read(2)
        if len(header) != 2:
            ser.timeout = restore_timeout
            return None

        msg = Msg(ser, MsgType(header[1]), header[0], None)

        if msg.length > 0:
            msg.content = ser.read(msg.length)
            if len(msg.content) != msg.length:
                ser.timeout = restore_timeout
                return None
            
        if ser.read() != b'\xff':
            ser.timeout = restore_timeout
            return None
        else:
            ser.timeout = restore_timeout
            return msg
        

class MsgFactory:
    def __init__(self, ser):
        self.ser = ser


    def createMessage(self, type: MsgType, length, content):
        return Msg(self.ser, type, length, content)
    

    def readMeassage(self):
        return Msg.read(self.ser)


class CommunicationModuleClass:
    def __init__(
            self, 
            onObject: Callable, 
            onAlertWeigth: Callable, 
            onAlertBump: Callable, 
            onAlertHum: Callable, 
            onAlertTemp: Callable,
            onStatusReceived: Callable,
            onIdReceived: Callable
        ):
        self.portname = ''
        self.ser = None
        self.message_factory = MsgFactory(self.ser)
        self.onObject: Callable = onObject
        self.onAlertWeigth: Callable = onAlertWeigth
        self.onAlertBump: Callable = onAlertBump
        self.onAlertHum: Callable = onAlertHum
        self.onAlertTemp: Callable = onAlertTemp
        self.onStatusReceived: Callable = onStatusReceived
        self.onIdReceived: Callable = onIdReceived


    def connect(self) -> bool:
        try:
            self.ser = serial.Serial(self.portname, timeout=0)
            self.message_factory.ser = self.ser
            return True
        except:
            self.ser = None
            self.message_factory.ser = self.ser
            return False
        

    def disconnect(self):
        self.ser = None
        self.message_factory.ser = self.ser


    def readPacket(self):
        msg = self.message_factory.readMeassage()
        if msg is not None:
            self.useMessage(msg)


    def useMessage(self, msg: Msg):
        if msg.type == MsgType.ALERT_WEIGHT:
            self.onAlertWeigth(int.from_bytes(msg.content, byteorder='little'))
            
        if msg.type == MsgType.ALERT_BUMP:
            self.onAlertBump()
        
        if msg.type == MsgType.ALERT_HUM:
            self.onAlertHum()

        if msg.type == MsgType.ALERT_TEMP:
            self.onAlertTemp(int.from_bytes(msg.content, byteorder='little'))

        if msg.type == MsgType.OBJ:
            uuid = msg.content.decode('ascii')
            self.onObject(uuid)

        if msg.type == MsgType.STATUS:
            if msg.length != 20:
                print('ERROR: wrong STATUS packet size')
            else:
                payload = msg.content

                error = bool.from_bytes(payload[0:4], 'little')
                temperature = int.from_bytes(payload[4:8], 'little')
                humidity = int.from_bytes(payload[8:12], 'little')
                acceleration = int.from_bytes(payload[12:16], 'little')
                weight = int.from_bytes(payload[16:20], 'little')

                self.onStatusReceived(error, temperature, humidity, acceleration, weight)

        if msg.type == MsgType.ID_ANSWER:
            self.onIdReceived(int.from_bytes(msg.content, 'little'))


    def sendWeightThreshold(self, weight_threshold: int):
        msg = self.message_factory.createMessage(MsgType.WEIGHT, 4, weight_threshold.to_bytes(byteorder='little', length=4))
        msg.send()


    def sendBumpThreshold(self, bump_threshold: int):
        msg = self.message_factory.createMessage(MsgType.BUMP, 4, bump_threshold.to_bytes(byteorder='little', length=4))
        msg.send()


    def sendTemperatureThreshold(self, temperature_min: int, temperature_max: int):
        msg = self.message_factory.createMessage(MsgType.TEMP, 8, temperature_min.to_bytes(byteorder='little', length=4) + temperature_max.to_bytes(byteorder='little', length=4))
        msg.send()


    def sendHumidityThreshold(self, humidity_threshold: int):
        msg = self.message_factory.createMessage(MsgType.HUM, 4, humidity_threshold.to_bytes(byteorder='little', length=4))
        msg.send()


    def sendTare(self, tare: int):
        msg = self.message_factory.createMessage(MsgType.TARE, 4, tare.to_bytes(byteorder='little', length=4))
        msg.send()
    

    def sendFindMe(self):
        if self.ser is not None:
            msg = self.message_factory.createMessage(MsgType.FIND_ME, 0, None)
            msg.send()


    def sendStopFindMe(self):
        if self.ser is not None:
            msg = self.message_factory.createMessage(MsgType.STOP_FIND_ME, 0, None)
            msg.send()


    def askBoxId(self) -> int:
        if self.ser is not None:
            msg = self.message_factory.createMessage(MsgType.ID_REQUEST, 0, None)
            msg.send()