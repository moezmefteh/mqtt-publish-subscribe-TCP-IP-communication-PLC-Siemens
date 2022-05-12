from ast import Str
import random
import time
from paho.mqtt import client as mqtt_client
from datetime import datetime

broker = 'localhost'
port = 1883
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'client0'
password = 'hivemq0'

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


def publish(client):
    msg_count = 0
    action=0
    while True:
        time.sleep(4)
        action=not(action)
        s=Str(action)
        msg = f"{msg_count}"
        temp=float(msg)+0.2
        result = client.publish("presion/cmd", msg)
        result = client.publish("msg/cmd", action)
        result = client.publish("action/cmd", action)
        result = client.publish("temp/cmd", temp)
        result = client.publish("motor/cmd", msg)

        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{'presion/cmd'}`")
            print(f"Send `{action}` to topic `{'msg/cmd'}`")
            print(f"Send `{action}` to topic `{'action/cmd'}`")
            print(f"Send `{temp}` to topic `{'temp/cmd'}`")
            print(f"Send `{msg}` to topic `{'motor/cmd'}`")

        else:
            print(f"Failed to send message ")
        msg_count += 1

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)

if __name__ == '__main__':
    run()

