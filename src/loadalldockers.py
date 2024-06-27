import os
import time
from datetime import date, timedelta
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
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


def start_all_dockers(thisdate,limits):
    logger = get_logger("dockerloader")
    logger.info("Building docker compose")
    getdate = thisdate
    os.system("docker build -t station .")
    c=1
    dcinside="version: '3'\nservices:\n"
    with open("docker-compose.yaml","w") as dcf:
        for filename in os.listdir(f"./rnxfiles/{getdate}"):
            if (filename[-3:]=="rnx"):
                c+=1
                dcinside+=f"  {filename[:4].lower()}:\n    volumes:\n    - type: bind\n      source: ./rnxfiles\n      target: /app/rnxfiles/\n    - type: bind\n      source: ./logs\n      target: /app/logs/\n    image: station:latest\n    command: python3 publisher.py {filename[:4].lower()}\n"
            if (c>int(limits)):
                break
        dcinside+=f"volumes:\n  rnxfiles:\n  logs:"
        dcf.write(dcinside)
    logger.info("Starting docker compose")
    os.system("docker compose up -d")
