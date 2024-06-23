import os
import time
from datetime import date, timedelta,datetime
import sys
import os
import requests
from sh import gunzip
import zipfile
import shutil
import hatanaka
from loadalldockers import start_all_dockers
from loadinfozip import start_loading
import logging
from logging.handlers import TimedRotatingFileHandler

FORMATTER_STRING = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./logs/rnxparser.log"

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)
    logger = logging.LoggerAdapter(logger)
    return logger

logger = get_logger("mainscript")
starttime=datetime.now()
thisdate=date.today()-timedelta(days=90)
logger.info("Start archive loading for date "+str(thisdate))
#start_loading(str(thisdate))
logger.info("Starting docker containers")
start_all_dockers(str(thisdate))
currenttime=datetime.now()
while True:
    time.sleep(60*21*20)
    starttime=datetime.now()
    thisdate+=timedelta(days=1)
    if (os.path.isdir("./rnxfiles/"+str(thisdate-timedelta(days=2)))):
        logger.info("Deleting old folder")
        shutil.rmtree(f'./rnxfiles/{str(thisdate-timedelta(days=2))}')
    logger.info("Loading new folder")
    start_loading(str(thisdate))
    currenttime=datetime.now()
    time.sleep(4*60*60-(currenttime-starttime).total_seconds())