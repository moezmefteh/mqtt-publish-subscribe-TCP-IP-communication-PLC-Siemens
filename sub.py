
from paho.mqtt import client as mqtt_client
import random

#params of pahoMQTT for pub and sub
broker = 'localhost'
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'client2'
password = 'client2'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    client.subscribe("action/cmd")
    client.on_message = on_message
    client.subscribe("presion/cmd")
    client.on_message = on_message
    client.subscribe("msg/cmd")
    client.on_message = on_message
    client.subscribe("temp/cmd")
    client.on_message = on_message

def run(): 
    client = connect_mqtt()
    subscribe(client)
    while True:
        client.loop_start()

if __name__ == '__main__':
    run()

