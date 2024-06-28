import sys
import os
import requests
from sh import gunzip
import zipfile
import shutil
from datetime import date, timedelta
import hatanaka
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import time

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


def archive_load(counter, getdate):
    link = f"https://api.simurg.space/datafiles/map_files?date={getdate}"
    filename = f"./downloadfiles/rnxfiles/{getdate}.zip"
    if counter>3:
        return False
    try:
        with open(filename, "wb") as f:
            response = requests.get(link, stream=True, timeout=60)
            total_length = response.headers.get('content-length')
            if total_length is None: # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                    sys.stdout.flush()
        return True
    except:
        time.sleep(30)
        return archive_load(counter+1, getdate)
    
def start_loading(thisdate):
    getdate = thisdate
    logger = get_logger("archiveloader")
    filename = f"./downloadfiles/rnxfiles/{getdate}.zip"
    logger.info("Downloading %s" % filename)
    res=archive_load(0, getdate)
    if (not(res)):
        logger.error("Downloading failed")
        return False
    logger.info("Extracting archive")
    with zipfile.ZipFile(filename, 'r') as zip_ref2:
            zip_ref2.extractall(path=filename.split(".zip")[0])
    logger.info("Converting .zip to .rnx")
    for gzfile in os.listdir(filename.split(".zip")[0]):
        hatanaka.decompress_on_disk(filename.split(".zip")[0]+"/"+gzfile)
    logger.info("Deleting archives")
    for file in os.listdir(filename.split(".zip")[0]):
        if (file[-2:]=="gz" or file[-2:]==".Z"):
            os.remove(filename.split(".zip")[0]+"/"+file)
    os.remove(filename)
    return True
