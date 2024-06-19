from datetime import date, timedelta
import os
import time
from time import gmtime, strftime  
import paho.mqtt.client as mqtt_client
import random
from gnss_tec import rnx
from sys import argv

def seconds_num(time):
    arrtime = time.split(":")
    return int(arrtime[0])*3600+int(arrtime[1])*60+int(arrtime[2])

def parseRNX(filename, clientid):
    with open(filename) as obs_file:
        reader = rnx(obs_file)
        tecit = reader.next_tec()
        tec=tecit.__next__()
        while seconds_num(strftime("%H:%M:%S", gmtime()))>seconds_num(tec.timestamp.strftime("%H:%M:%S")):
            tec=tecit.__next__()
        broker="broker.emqx.io"
        client = mqtt_client.Client(
            mqtt_client.CallbackAPIVersion.VERSION1, 
            'dfewfwetrewf'
        )
        print("Connecting to broker",broker)
        print(client.connect(broker))
        print("Publishing")
        client.loop_start() 
        while tec.timestamp.strftime("%H:%M:%S")!='23:59:30':
            result = filename+" "+tec.timestamp.strftime("%H:%M:%S")+'\n'
            prevtec=tec
            while tec.timestamp.strftime("%H:%M:%S") == prevtec.timestamp.strftime("%H:%M:%S"):
                prevtec=tec
                result+='{}: {} {}'.format(tec.satellite, tec.phase_tec, tec.p_range_tec,)+'\n'
                tec = tecit.__next__()
            client.publish("lab/leds/state",result)
            print(result)
            time.sleep(30)
        client.disconnect()
        client.loop_stop()



script, filename, clientid=argv
parseRNX(filename, clientid)
