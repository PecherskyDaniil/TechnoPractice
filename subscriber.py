#subscriber
import struct
import time
import datetime
#pip install paho-mqtt
import paho.mqtt.client as mqtt_client
import random
import matplotlib.pyplot as plt

client_id=#your client_id
topic=#your topic
broker="sdb777f7.ala.dedicated.aws.emqxcloud.com"

def on_message(client, userdata, message):
    print(len(message.payload))
    bytelen=(len(message.payload)-4)//13
    print(bytelen)
    sf=">L"
    for i in range(bytelen):
        sf+="ciff"
    data = struct.unpack(sf,message.payload)
    date = datetime.datetime.fromtimestamp(data[0]-8*60*60)
    print(date.strftime("%H:%M:%S"))
    mainarr=[]
    for i in range(1,len(data),4):
        mainarr+=[data[i].decode()+str(data[i+1])+":"+str(data[i+2])+", "+str(data[i+3])]
    sats = list(map(lambda x:x.split(":")[0], mainarr))
    sd = list(map(lambda x:float(x.split(":")[1].split(", ")[0]), mainarr))
    fig, ax = plt.subplots()
    ax.bar(sats, sd)
    plt.show(block=False)
    plt.pause(29)
    plt.close(fig)

#client = mqtt_client.Client('isu100123123123')
# FOR new version change ABOVE line to 
client = mqtt_client.Client(
    mqtt_client.CallbackAPIVersion.VERSION1, 
    client_id
)
client.username_pw_set("admin", "admin")
client.on_message=on_message

print("Connecting to broker",broker)
client.connect(broker) 
client.loop_start() 
print("Subcribing")
client.subscribe("stations/"+topic)
time.sleep(1800)
client.disconnect()
client.loop_stop()
