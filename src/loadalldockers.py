import os
import time
from datetime import date, timedelta
def start_all_dockers(thisdate):
    getdate = thisdate
    os.system("docker build -t station .")
    if (not(os.path.isfile("docker-compose.yaml"))):
        dcinside="version: '3'\nservices:\n"
        with open("docker-compose.yaml","w") as dcf:
            for filename in os.listdir(f"./rnxfiles/{getdate}"):
                if (filename[-3:]=="rnx"):
                    dcinside+=f"  {filename[:4].lower()}:\n    volumes:\n    - type: bind\n      source: ./rnxfiles\n      target: /app/rnxfiles/\n    - type: bind\n      source: ./logs\n      target: /app/logs/\n    image: station:latest\n    command: python3 publisher.py {filename[:4].lower()}\n"
            dcinside+=f"volumes:\n  rnxfiles:\n  logs:"
            dcf.write(dcinside)
    os.system("docker compose up -d")
