from fastapi import Depends, FastAPI, HTTPException, Request
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import subprocess
 

app = FastAPI()

@app.get("/streams/")
def getstreams():
    command = "docker ps -a | grep -v 'Exited'|grep -o '\-.*\-'|sed 's/-//g'"
    result = {"streams":subprocess.check_output(command, shell=True, text=True).split("\n")[:-1]}
    return result