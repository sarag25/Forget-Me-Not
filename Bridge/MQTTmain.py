from time import sleep
from MQTTModule import MQTTModuleClass

def onObjMove(objId):
    print('main received that ' + str(objId) + ' object has moved')

if __name__ == '__main__':
    mqtt1 = MQTTModuleClass(1, onObjMove, [1, 2, 3])
    mqtt2 = MQTTModuleClass(2, onObjMove, [4, 5])

    sleep(1)
    mqtt2.publish_obj(2)

    sleep(1)
    mqtt1.publish_obj(2)

    sleep(1)
    mqtt1.publish_box_user(1)

    sleep(1)
    mqtt2.publish_box_user(2)

    sleep(1)
    mqtt1.publish_box_position(10.84765, 156.2837)

    sleep(1)
    mqtt1.publish_box_serie(False, 20, 50, 70, 2000)

    while True:
        pass