from fastapi import Depends, FastAPI, HTTPException, Request
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import subprocess
import os
from datetime import datetime
app = FastAPI()

@app.get("/topics/")
def getstreams():
    command = "docker ps | grep -v 'Exited'|grep -o '\-.*\-'|sed 's/-//g'"
    result = {"topics":subprocess.check_output(command, shell=True, text=True).split("\n")[:-1]}
    return result

@app.post("/launch/")
def launchscript(limit:int=1000):
    command = "docker ps | grep -v 'Exited'|grep -o '\-.*\-'|sed 's/-//g'"
    result = subprocess.check_output(command, shell=True, text=True).split("\n")[:-1]
    if (len(result)>0):
        return {"status":"already launched"}
    else:
    	os.system(f"python3 mainscript.py {limit} &")
    	return {"status":"started"}

@app.get("/streams/status")
def getstreamsstatus():
    statuses={"streams":[]}
    curtime=datetime.now()
    command1 = "docker ps | grep -v 'Exited'|grep -o '\-.*\-'|sed 's/-//g'"
    topics = subprocess.check_output(command1, shell=True, text=True).split("\n")[:-1]
    for topic in topics:
        command2=f"grep {topic} ./logs/rnxparser.log | tail -1"
        result=subprocess.check_output(command2, shell=True, text=True)
        dttime=datetime.strptime(result[:19], '%Y-%m-%d %H:%M:%S')
        if "Script started" in result or "Searching file" in result or "File found" in result or "Opening file" in result or "File opened" in result or "Connecting to broker" in result or "Connected to broker" in result or "Parsing started" in result or "Parsing tec-records with time" in result:
            statuses["streams"].append({"name":topic,"status":"Launching"})
        elif "Publishing tec-records" in result or "Waiting 30 seconds" in result and (dttime-curtime).total_seconds()<60:
            statuses["streams"].append({"name":topic,"status":"Working"})
        else:
            statuses["streams"].append({"name":topic,"status":"Stopped"})
    return statuses
@app.post("/stop/")
def stopscript():
    command = "docker ps | grep -v 'Exited'|grep -o '\-.*\-'|sed 's/-//g'"
    result = subprocess.check_output(command, shell=True, text=True).split("\n")[:-1]
    if (len(result)>0):
        os.system("docker stop $(docker ps | grep -v 'Exited'|grep -o 'src\-.*\-1')")
        os.system("kill $(ps -a|grep python3| cut -d ' ' -f 3)")
        return {"status":"stopped"}
    else:
    	return {"status":"nothing to stop"}