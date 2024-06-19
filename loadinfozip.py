import sys
import os
import requests
from sh import gunzip
import zipfile
import shutil
from datetime import date, timedelta
import hatanaka
getdate = str(date.today() - timedelta(days=60))

link = f"https://api.simurg.space/datafiles/map_files?date={getdate}"
file_name = f"./{getdate}.zip"
with open(file_name, "wb") as f:
    print("Downloading %s" % file_name)
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
filepath=f"./{getdate}.zip"
with zipfile.ZipFile(filepath, 'r') as zip_ref2:
        zip_ref2.extractall(path=filepath.split(".zip")[0])
for gzfile in os.listdir(filepath.split(".zip")[0]):
     hatanaka.decompress_on_disk(filepath.split(".zip")[0]+"/"+gzfile)
for file in os.listdir(filepath.split(".zip")[0]):
     if (file[-2:]=="gz" or file[-2:]==".Z"):
          os.remove(filepath.split(".zip")[0]+"/"+file)
os.remove(filepath)