from fastapi import Depends, FastAPI, HTTPException, Request
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import subprocess
import os
from datetime import datetime
app = FastAPI()

FORMATTER_STRING = "%(asctime)s - %(name)s - %(request)s - %(levelname)s - %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./logs/rnxparser.log"

def get_logger(logger_name,request):
    extra = {'request':request}
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

@app.get("/topics/")
def getstreams():
    logger=get_logger("fastapi","getstreams")
    logger.info("User requested topics")
    try:
        command = "docker ps | grep -v 'Exited'|grep -o '\-.*\-'|sed 's/-//g'"
        result = {"topics":subprocess.check_output(command, shell=True, text=True).split("\n")[:-1]}
    except:
        logger.error("Command execution was failed")
    logger.debug("Topics returned")
    return result

@app.post("/launch/")
def launchscript(limit:int=1000):
    logger=get_logger("fastapi","launchscript")
    logger.info("User launched scripts")
    try:
        command = "docker ps | grep -v 'Exited'|grep -o '\-.*\-'|sed 's/-//g'"
        result = subprocess.check_output(command, shell=True, text=True).split("\n")[:-1]
    except:
        logger.error("Command execution was failed")
    if (len(result)>0):
        logger.debug("Scripts already launched")
        return {"status":"already launched"}
    else:
    	os.system(f"python3 ./mainscript.py {limit} &")
    	logger.debug("Scripts started")
    	return {"status":"started"}

@app.get("/streams/status")
def getstreamsstatus():
    logger=get_logger("fastapi","getstreamstatus")
    logger.info("User requested stream statuses")
    statuses={"streams":[]}
    curtime=datetime.now()
    try:
        command1 = "docker ps | grep -v 'Exited'|grep -o '\-.*\-'|sed 's/-//g'"
        topics = subprocess.check_output(command1, shell=True, text=True).split("\n")[:-1]
    except:
        logger.error("Command execution was failed")
    for topic in topics:
        command2=f"grep {topic} ./logs/rnxparser.log | tail -1"
        result=subprocess.check_output(command2, shell=True, text=True)
        dttime=datetime.strptime(result[:19], '%Y-%m-%d %H:%M:%S')
        if "Script started" in result or "Searching file" in result or "File found" in result or "Opening file" in result or "File opened" in result or "Connecting to broker" in result or "Connected to broker" in result or "Parsing started" in result or "Parsing tec-records with time" in result:
            statuses["streams"].append({"name":topic,"status":"Launching"})
        elif "Message Published" in result and (dttime-curtime).total_seconds()<60:
            statuses["streams"].append({"name":topic,"status":"Working"})
        else:
            statuses["streams"].append({"name":topic,"status":"Stopped"})
    logger.debug("Statuses returned")
    return statuses

@app.post("/stop/")
def stopscript():
    logger=get_logger("fastapi","stopscript")
    logger.info("User stops script")
    try:
        command = "docker ps | grep -v 'Exited'|grep -o '\-.*\-'|sed 's/-//g'"
        result = subprocess.check_output(command, shell=True, text=True).split("\n")[:-1]
    except:
        logger.error("Command execution was failed")
    if (len(result)>0):
        os.system("docker stop $(docker ps | grep -v 'Exited'|grep -o 'src\-.*\-1')")
        os.system("kill $(ps -a|grep python3|sed 's/^[ \t]*//'|cut -d " " -f 1)")
        logger.debug("Script stopped")
        return {"status":"stopped"}
    else:
        logger.debug("Nothing to stop")
    	return {"status":"nothing to stop"}
