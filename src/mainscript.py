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
thisdate=date.today()-timedelta(days=90)
start_loading(str(thisdate))
start_all_dockers(str(thisdate))
currenttime=datetime.now()
while True:
    time.sleep(60*21*20)
    starttime=datetime.now()
    thisdate+=timedelta(days=1)
    if (os.path.isdir("./rnxfiles/"+str(thisdate-timedelta(days=2)))):
        shutil.rmtree(f'./rnxfiles/{str(thisdate-timedelta(days=2))}')
    start_loading(str(thisdate))
    currenttime=datetime.now()
    time.sleep(4*60*60-(currenttime-starttime).total_seconds())