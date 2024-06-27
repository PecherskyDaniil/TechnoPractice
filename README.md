# TechnoPractice


## Описание проекта

Данный репозиторий хранит файлы для запуска собственного сервера публикующего сообщений из rnx файлов полученных с SIMURG. Данный сервер запускает скрипты имитирующие безостановочную (пока не будет остановлено вручную или из-за проблем, независящих от авторов проекта) отправку сообщений со станций.


## Описание работы проекта

Полная схема работы данного сервера понятно и наглядно описана в диаграммах. Если вкратце: все управляется из сервера на fastapi, с помощью отправки запросов на который происходит запуск и мониторинг основных процессов. После запуска, программа автоматически скачивает архив с rnx файлами и создает докер контейнеры, в кождом из которых независимо работают скрипты, публикующие сообщения из файлов. Каждый скрипт непрерывно публикует сообщения и ищет новые файлы при окончании прошлых. Главный скрипт также непрерывно работает, скачивая новые архивы при необходимости. Для мониторинга работы этой программы следует использовать соответсвующие запросы на fastapi сервер, описанные ниже.

![image](https://github.com/PecherskyDaniil/TechnoPractice/assets/78026424/8762b563-c5e3-42b8-b458-a8a748485a8c)
![image](https://github.com/PecherskyDaniil/TechnoPractice/assets/78026424/12f936f2-0223-42fd-8d9a-1f2d2ed90fe0)
![image](https://github.com/PecherskyDaniil/TechnoPractice/assets/78026424/6fd1ae7d-b386-46ef-ac2d-933008037104)

## Запуск проекта

Для запуска проекта следует иметь на машине docker, docker-compose, fastapi, uvicorn и python. Сама машина должна быть на Linux, иначе некоторые функции (а возможно и весь проект) работать не будут. После установки всех перечисленных компонентов установите библиотеки для python, прописав следующую команду в корневой папке проекта:
```
pip install -r requirements.txt
```
Для запуска веб-сервера на fastapi используйте эту команду находясь в папке src:
```
uvicorn fastapiscript:app --host 0.0.0.0 --port 8000
```
После этого зайдите в браузере на страницу http://*ip вашей машины*/docs где удобнее управлять запросами.

## Запросы на сервер
### Запуск проекта
```/launch/```
Success Response
```
{"status":"started"}
```
Fail Response
```
{"status":"already launched"}
```

### Остановка проекта
```/stop/```
Success Response
```
{"status":"stopped"}
```
Fail Response
```
{"status":"nothing to stop"}
```

### Список топиков
```/topics/```
Response
```
{"topics":["abcd","efgh","jame"]}
```

### Статусы потоков
```/streams/status/```
Response
```
{"streams":[{"name":"abcd","status":"Working"},{"name":"jfdg","status":"Launching"},{"name":"olad","status":"Stopped"}]}
```
## Работа с получаемыми данными
Для получения и парсинга данных можно использовать следующую программу, рисующую графики полученных данных из определенного потока. Также эта программа лежит в самом репозитории, с названием "subscriber.py". При запуске не забудьте указать client_id и topic. Список topic можно получить из соответствующего запроса в API, а client_id может быть любая уникальная(!) строка.
```
#subscriber
import struct
import time
import datetime
#pip install paho-mqtt
import paho.mqtt.client as mqtt_client
import random
import matplotlib.pyplot as plt

client_id=#your client_id
topic=#your topic
broker="sdb777f7.ala.dedicated.aws.emqxcloud.com"

def on_message(client, userdata, message):
    print(len(message.payload))
    bytelen=(len(message.payload)-4)//13
    print(bytelen)
    sf=">L"
    for i in range(bytelen):
        sf+="ciff"
    data = struct.unpack(sf,message.payload)
    date = datetime.datetime.fromtimestamp(data[0]-8*60*60)
    print(date.strftime("%H:%M:%S"))
    mainarr=[]
    for i in range(1,len(data),4):
        mainarr+=[data[i].decode()+str(data[i+1])+":"+str(data[i+2])+", "+str(data[i+3])]
    sats = list(map(lambda x:x.split(":")[0], mainarr))
    sd = list(map(lambda x:float(x.split(":")[1].split(", ")[0]), mainarr))
    fig, ax = plt.subplots()
    ax.bar(sats, sd)
    plt.show(block=False)
    plt.pause(29)
    plt.close(fig)

#client = mqtt_client.Client('isu100123123123')
# FOR new version change ABOVE line to 
client = mqtt_client.Client(
    mqtt_client.CallbackAPIVersion.VERSION1, 
    client_id
)
client.username_pw_set("admin", "admin")
client.on_message=on_message

print("Connecting to broker",broker)
client.connect(broker) 
client.loop_start() 
print("Subcribing")
client.subscribe("stations/"+topic)
time.sleep(1800)
client.disconnect()
client.loop_stop()
```
