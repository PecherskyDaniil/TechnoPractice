from datetime import date, timedelta
import datetime
import os
import time
from time import gmtime, strftime  
import paho.mqtt.client as mqtt_client
import random
from gnss_tec import rnx
from sys import argv
import sys
import threading
import logging
from logging.handlers import TimedRotatingFileHandler
import struct

FORMATTER_STRING = "%(asctime)s - %(stationname)s - %(name)s - %(levelname)s - %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./logs/rnxparser.log"
script, stationname=argv   

def get_logger(logger_name,stationname):
    extra = {'stationname':stationname}
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)
    logger = logging.LoggerAdapter(logger, extra)
    return logger

getdate=date.today() - timedelta(days=90)
logger = get_logger("publisher",stationname)
logger.info("Script started")

def seconds_num(time):
    arrtime = time.split(":")
    return int(arrtime[0])*3600+int(arrtime[1])*60+int(arrtime[2])

event=False

def on_publish(client, userdata, mid):
    logger.debug("Message Published")

def intervalPublish(tecit, curtec, client, fn, file):
    global event
    tec=curtec
    timer=threading.Timer(30.0, lambda: intervalPublish(tecit, tec, client, fn, file))
    timer.start()
    result = struct.pack(">L",int(tec.timestamp.timestamp()))
    prevtec=tec
    logger.debug("Parsing tec-records with time "+ tec.timestamp.strftime("%H:%M:%S"))
    while tec.timestamp.strftime("%H:%M:%S") == prevtec.timestamp.strftime("%H:%M:%S"):
        prevtec=tec
        if tec.phase_tec!=None:
            phase_tec=float(tec.phase_tec)
        else:
            phase_tec=0
        if tec.p_range_tec!=None:
            p_range_tec=float(tec.p_range_tec)
        else:
            p_range_tec=0
        result+=struct.pack(">ciff",tec.satellite[0].encode(),int(tec.satellite[1:]) , phase_tec, p_range_tec)
        try:
            tec=tecit.__next__()
        except:
            client.disconnect()
            file.close()
            event=True
            return
    client.publish("stations/"+stationname,result)

def parseRNX(filename, clientid):
    global event
    logger.debug("Opening file")
    try:
        obs_file=open(filename)
        logger.debug("File opened")
    except:
        logger.error("File cannot be opened")
    reader = rnx(obs_file)
    tecit = reader.next_tec()
    tec = tecit.__next__()
    curtime = datetime.datetime.now().strftime("%H:%M:%S")
    while seconds_num(curtime)>seconds_num(tec.timestamp.strftime("%H:%M:%S")):
        tec=tecit.__next__()
    broker="sdb777f7.ala.dedicated.aws.emqxcloud.com"
    username="admin"
    password="admin"
    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION1, 
        clientid
    )
    client.username_pw_set(username, password)
    client.on_publish=on_publish
    logger.debug("Connecting to broker "+broker)
    try:
        client.connect(broker)
        logger.debug("Connected to broker")
    except:
        logger.error("Cannot connect to broker")
    starttime=min(60-int(datetime.datetime.now().strftime("%S")),abs(30-int(datetime.datetime.now().strftime("%S"))))-0.5
    time.sleep(starttime)
    logger.info("Parsing started") 
    intervalPublish(tecit, tec, client, filename, obs_file)
    while True:
        if event:
            break

          

while True:
    filename=""
    logger.debug("Searching file")
    try:
        for filen in os.listdir(f"./rnxfiles/{str(getdate)}"):
            if (filen[:4].lower()==stationname):
                filename=f"./rnxfiles/{str(getdate)}/{filen}"
                break
    except:
        logger.debug("Folder not found")
        time.sleep(30)
        continue
    if filename!="":
        logger.debug("File found")
        event=False
        parseRNX(filename, stationname)
    else:
        logger.debug("File not found")
        time.sleep(30)
        continue
    getdate=getdate+timedelta(days=1)
    logger.debug("Switched date to "+str(getdate))
