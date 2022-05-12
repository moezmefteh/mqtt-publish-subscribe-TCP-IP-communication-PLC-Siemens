import snap7
from snap7.util import get_string,get_int,get_bool
from paho.mqtt import client as mqtt_client
import threading
import random

#params of the PLC for snap7
IP = '192.168.0.10'
RACK = 0
SLOT = 1
DB_NUMBER = 2
START_ADDRESS = 0
SIZE = 266
#params of pahoMQTT for pub and sub
broker = 'localhost'
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'client1'
password = 'client1'

#init PLC
plc = snap7.client.Client()
plc.connect(IP,RACK,SLOT)
plc_info = plc.get_cpu_info()
print(f'Module Type: {plc_info.ModuleTypeName}')
state = plc.get_cpu_state()
print(f'State: {state}')
#read PLC_DB
db = plc.db_read(DB_NUMBER,START_ADDRESS,SIZE)
presion0 = get_int(db,0)
print(f'presion: {presion0}')
msg0 = get_string(db[0:255], 2, 258)
print(f'msg: {msg0}')
action0 = get_bool(db,258,0)
print(f'action: {action0}')


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

def publish(client,topic,msg):
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send '{msg}' to topic `{topic}`")
    else:
        print(f"Failed to send message to topic '{topic}'")

client = connect_mqtt()


while True:

    db = plc.db_read(DB_NUMBER,START_ADDRESS,SIZE)
    presion = get_int(db,0)
    if(presion!=presion0):
        presion0=presion
        publish(client,"presion",presion)
        print(f'presion: {presion}')

    msg = get_string(db[0:255], 2, 258) 
    if(msg!=msg0):
        msg0=msg
        publish(client,"msg",msg)
        print(f'msg: {msg}')

    action = get_bool(db,258,0)
    if(action!=action0):
        action0=action
        publish(client,"action",action)
        print(f'action: {action}')

        