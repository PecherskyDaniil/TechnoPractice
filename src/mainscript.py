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

starttime=datetime.now()
thisdate=str(date.today()-timedelta(days=90))
start_loading(thisdate)
start_all_dockers(thisdate)
currenttime=datetime.now()
while True:
    time.sleep(60*60*21)
    starttime=datetime.now()
    thisdate+=timedelta(days=1)
    start_loading(thisdate)
    currenttime=datetime.now()
    time.sleep(3*60*60-(currenttime-starttime).total_seconds)