from time import sleep
from backend import Box

if __name__ == '__main__':
    box = Box()
    connected = False
    while not connected:
        conn = box.connect('/dev/rfcomm0')
        if conn['Status'] == True:
            connected = True
        sleep(0.2)
    
    print('Connection established')
    print('THRESHOLDS:\n\ttempMin:' + str(box.temperature_min) + '\n\ttempMax:' + str(box.temperature_max) + '\n\tweight threshold: ' + str(box.weight_threshold) + '\n\tbump threshold: ' + str(box.acceleration_threshold) + '\n\thumidity threshold: ' + str(box.humidity_threshold))

    prevToolList = box.getToolsList()
    print('Tool list iniziale')
    print(prevToolList)
    prevErrorList = box.getErrorList()

    while True:
        conn, toolList, errorList = box.update()
        if toolList != prevToolList:
            print('La lista dei tool è cambiata')
            print(toolList)
            prevToolList = toolList
        if errorList != prevErrorList:
            print('La lista degli errori è cambiata')
            print(errorList)
            prevErrorList = errorList
            