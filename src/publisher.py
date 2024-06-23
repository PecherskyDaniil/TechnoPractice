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

FORMATTER_STRING = "%(asctime)s - %(stationname)s - %(name)s - %(levelname)s - %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./logs/rnxparser.log"

starttime=min(60-int(datetime.datetime.now().strftime("%S")),abs(30-int(datetime.datetime.now().strftime("%S"))))
time.sleep(starttime)    

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
print(getdate)
def seconds_num(time):
    arrtime = time.split(":")
    return int(arrtime[0])*3600+int(arrtime[1])*60+int(arrtime[2])

event=False

def intervalPublish(tecit, curtec, client, fn, file):
    global event
    tec=curtec
    timer=threading.Timer(30.0, lambda: intervalPublish(tecit, tec, client, fn, file))
    timer.start()
    result = fn+" "+tec.timestamp.strftime("%H:%M:%S")+'\n'
    prevtec=tec
    logger.info("Parsing tec-records with time "+ tec.timestamp.strftime("%H:%M:%S"))
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
    logger.info("Publishing tec-records")
    client.publish("lab/leds/state",result)
    print(result)
    logger.info("Waiting 30 seconds")

def parseRNX(filename, clientid, logger):
    global event
    logger.debug("Opening file")
    try:
        obs_file=open(filename)
        logger.debug("File opened")
    except:
        logger.error("File cannot be opened")
    reader = rnx(obs_file)
    tecit = reader.next_tec()
    tec=tecit.__next__()
    #while seconds_num("23:57:00")>seconds_num(tec.timestamp.strftime("%H:%M:%S")):
    #    tec=tecit.__next__()
    broker="sdb777f7.ala.dedicated.aws.emqxcloud.com"
    username="admin"
    password="admin"
    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION1, 
        clientid
    )
    client.username_pw_set(username, password)
    logger.debug("Connecting to broker "+broker)
    try:
        client.connect(broker)
        logger.debug("Connected to broker")
    except:
        logger.error("Cannot connect to broker")
    logger.info("Parsing started") 
    intervalPublish(tecit, tec, client, filename, obs_file)
    while True:
        if event:
            break

          
script, stationname=argv
logger = get_logger("publisher",stationname)
logger.info("Script started")
while True:
    filename=""
    logger.info("Searching file")
    try:
        for filen in os.listdir(f"./rnxfiles/{str(getdate)}"):
            if (filen[:4].lower()==stationname):
                filename=f"./rnxfiles/{str(getdate)}/{filen}"
                break
    except:
        logger.info("Folder not found")
        time.sleep(30)
        continue
    if filename!="":
        logger.info("File found")
        event=False
        parseRNX(filename, stationname, logger)
    else:
        logger.info("File not found")
        time.sleep(30)
        continue
    getdate=getdate+timedelta(days=1)
    logger.info("Switched date to "+str(getdate))