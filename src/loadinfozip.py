import sys
import os
import requests
from sh import gunzip
import zipfile
import shutil
from datetime import date, timedelta
import hatanaka
def start_loading(thisdate):
    getdate = thisdate

    link = f"https://api.simurg.space/datafiles/map_files?date={getdate}"
    filename = f"./rnxfiles/{getdate}.zip"
    with open(filename, "wb") as f:
        print("Downloading %s" % filename)
        response = requests.get(link, stream=True)
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

    with zipfile.ZipFile(filename, 'r') as zip_ref2:
            zip_ref2.extractall(path=filename.split(".zip")[0])
    for gzfile in os.listdir(filename.split(".zip")[0]):
        hatanaka.decompress_on_disk(filename.split(".zip")[0]+"/"+gzfile)
    for file in os.listdir(filename.split(".zip")[0]):
        if (file[-2:]=="gz" or file[-2:]==".Z"):
            os.remove(filename.split(".zip")[0]+"/"+file)
    os.remove(filename)
    return True
