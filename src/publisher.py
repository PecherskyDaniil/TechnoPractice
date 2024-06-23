from datetime import date, timedelta
import os
import time
from time import gmtime, strftime  
import paho.mqtt.client as mqtt_client
import random
from gnss_tec import rnx
from sys import argv
import threading

getdate=date.today() - timedelta(days=90)

def seconds_num(time):
    arrtime = time.split(":")
    return int(arrtime[0])*3600+int(arrtime[1])*60+int(arrtime[2])

event=False

def intervalPublish(tecit, curtec, client, fn, file):
    global event
    tec=curtec
    result = fn+" "+tec.timestamp.strftime("%H:%M:%S")+'\n'
    prevtec=tec
    while tec.timestamp.strftime("%H:%M:%S") == prevtec.timestamp.strftime("%H:%M:%S"):
        prevtec=tec
        result+='{}: {} {}'.format(tec.satellite, tec.phase_tec, tec.p_range_tec,)+'\n'
        try:
            tec=tecit.__next__()
        except:
            client.disconnect()
            file.close()
            print("end")
            event=True
            return
    client.publish("lab/leds/state",result)
    print(result)
    timer=threading.Timer(30.0, lambda: intervalPublish(tecit, tec, client, fn, file))
    timer.start()

def parseRNX(filename, clientid):
    global event
    obs_file=open(filename)
    reader = rnx(obs_file)
    tecit = reader.next_tec()
    tec=tecit.__next__()
    #while seconds_num("23:57:00")>seconds_num(tec.timestamp.strftime("%H:%M:%S")):
    #    tec=tecit.__next__()
    broker=#your broker
    username=#your username
    password=#your password
    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION1, 
        clientid
    )
    client.username_pw_set(username, password)
    print("Connecting to broker",broker)
    print(client.connect(broker))
    print("Publishing") 
    intervalPublish(tecit, tec, client, filename, obs_file)
    while True:
        if event:
            break

          
script, stationname=argv
while True:
    filename=""
    for filen in os.listdir(f"/app/rnxfiles/{str(getdate)}"):
        if (filen[:4].lower()==stationname):
            filename=f"/app/rnxfiles/{str(getdate)}/{filen}"
            break
    if filename!="":
        event=False
        parseRNX(filename, stationname)
    else:
        time.sleep(30)
        continue
    getdate=getdate+timedelta(days=1)
