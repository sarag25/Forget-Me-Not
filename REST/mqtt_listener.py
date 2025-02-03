from flask_mqtt import Mqtt
import requests
import json

mqtt = Mqtt()

# ! restart and double messages if debug mode active in config.py

# On connection subscribes to the mqtt topics 
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt.subscribe('/boxes/#')
        mqtt.subscribe('/tools/#')    
    else:
        print('Bad connection. Code:', rc)

# On message checks the topic and issues the appropriate REST request
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

    print('Received message on topic: {topic} with payload: {payload}\n'.format(**data))

    if 'id_operator' in data['topic']:
       url="http://localhost" + data['topic']
       d = {'id': data['payload']}
       r = requests.put(url, json=json.loads(json.dumps(d)), headers={'Content-type': 'application/json'})
       
    elif 'temporal_serie' in data['topic']:
       url="http://localhost" + data['topic']
       r = requests.post(url, json=json.loads(data['payload']), headers={'Content-type': 'application/json'})

    elif 'position' in data['topic']:
        url="http://localhost" + data['topic']
        #d = json.dumps(data['payload'])
        r = requests.put(url, json=json.loads(data['payload']), headers={'Content-type': 'application/json'})
       
    elif 'tools' in data['topic']:
       url="http://localhost" + data['topic']
       d = {'id_box': data['payload']}
       r = requests.put(url, json=json.loads(json.dumps(d)), headers={'Content-type': 'application/json'})
