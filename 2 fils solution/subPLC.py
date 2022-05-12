import snap7
from snap7.util import get_string,get_int,get_bool
from paho.mqtt import client as mqtt_client
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
username = 'client2'
password = 'client2'

#init PLC
plc = snap7.client.Client()
plc.connect(IP,RACK,SLOT)
plc_info = plc.get_cpu_info()
print(f'Module Type: {plc_info.ModuleTypeName}')
state = plc.get_cpu_state()
print(f'State: {state}')
#read PLC_DB
db = plc.db_read(DB_NUMBER,START_ADDRESS,SIZE)

def Send_Bool_To_PLC(value):
    snap7.util.set_bool(db,258,0,value)
    plc.db_write(DB_NUMBER,START_ADDRESS,db)
def Send_Int_To_PLC(value):
    snap7.util.set_int(db,0,value)
    plc.db_write(DB_NUMBER,START_ADDRESS,db)
def Send_String_To_PLC(value):
    snap7.util.set_string(db,2,value,256)
    plc.db_write(DB_NUMBER,START_ADDRESS,db)
def Send_Real_To_PLC(value):
    snap7.util.set_real(db,260,value)
    plc.db_write(DB_NUMBER,START_ADDRESS,db)

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
        if(msg.topic=='action/cmd'):
            Send_Bool_To_PLC(bool (msg.payload.decode()))
        if(msg.topic=='presion/cmd'):
            Send_Int_To_PLC(int (msg.payload.decode()))
        if(msg.topic=='msg/cmd'):
            Send_String_To_PLC(msg.payload.decode())
        if(msg.topic=='temp/cmd'):
            Send_Real_To_PLC(float(msg.payload.decode()))
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

