import snap7
from snap7.util import get_string,get_int,get_bool,get_real
from paho.mqtt import client as mqtt_client
import random

#params of the PLC for snap7
IP = '192.168.0.5'
RACK = 0
SLOT = 1
DB_NUMBER=2
START_ADDRESS=0
SIZE=266
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
temp0 = get_real(db,260)
print(f'temp: {temp0}')
motor0 = get_int(db,264)
print(f'motor: {motor0}')

def Send_Bool_To_PLC(value):
    snap7.util.set_bool(db,258,0,value)
    plc.db_write(DB_NUMBER,START_ADDRESS,db)

def Send_Int_To_PLC(adress,value):
    snap7.util.set_int(db,adress,value)
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

def publish(client,topic,msg):
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send '{msg}' to topic `{topic}`")
    else:
        print(f"Failed to send message to topic '{topic}'")

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if(msg.topic=='presion/cmd'):
            Send_Int_To_PLC(0,int (msg.payload.decode()))
        if(msg.topic=='action/cmd'):
            Send_Bool_To_PLC(bool (msg.payload.decode()))
        if(msg.topic=='msg/cmd'):
            Send_String_To_PLC(msg.payload.decode())
        if(msg.topic=='temp/cmd'):
            Send_Real_To_PLC(float(msg.payload.decode()))
        if(msg.topic=='motor/cmd'):
            Send_Int_To_PLC(264,int (msg.payload.decode()))            
    client.subscribe("action/cmd")
    client.on_message = on_message
    client.subscribe("presion/cmd")
    client.on_message = on_message
    client.subscribe("msg/cmd")
    client.on_message = on_message
    client.subscribe("msg/cmd")
    client.on_message = on_message
    client.subscribe("temp/cmd")
    client.on_message = on_message
    client.subscribe("motor/cmd")
    client.on_message = on_message

client = connect_mqtt()
subscribe(client)

while True:
    client.loop(.1)

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

    temp = get_real(db,260)
    if(temp!=temp0):
        temp0=temp
        publish(client,"temp",temp)
        print(f'temp: {temp}')

    motor = get_int(db,264)
    if(motor!=motor0):
        motor0=motor
        publish(client,"motor",motor)
        print(f'motor: {motor}')