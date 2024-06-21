import os
import time
from datetime import date, timedelta
getdate = str(date.today() - timedelta(days=90))
os.system("docker build -t station .")
time.sleep(20)
dcinside="version: '3'\nservices:\n"
with open("docker-compose.yaml","w") as dcf:
    for filename in os.listdir(f"./rnxfiles/{getdate}"):
        if (filename[-3:]=="rnx"):
           dcinside+=f"  {filename[:4].lower()}:\n    volumes:\n    - type: bind\n      source: ./rnxfiles\n      target: /app/rnxfiles/\n    image: station:latest\n    command: python3 publisher.py {filename[:4].lower()}\n"
    dcinside+=f"volumes:\n  rnxfiles:"
    dcf.write(dcinside)
os.system(f"docker compose up")