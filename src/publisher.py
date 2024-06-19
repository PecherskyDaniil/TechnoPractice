import time
import paho.mqtt.client as mqtt_client
import random
from gnss_tec import rnx
from sys import argv


script, filename, clientid=argv
broker="broker.emqx.io"

#client = mqtt_client.Client('isu100123234235')
# FOR new version change ABOVE line to 
client = mqtt_client.Client(
    mqtt_client.CallbackAPIVersion.VERSION1, 
    clientid
)

print("Connecting to broker",broker)
print(client.connect(broker))
client.loop_start() 
print("Publishing")

with open(filename) as obs_file:
    reader = rnx(obs_file)
    for tec in reader:
        client.publish("lab/leds/state",
            '{} {}: {} {}'.format(
                tec.timestamp,
                tec.satellite,
                tec.phase_tec,
                tec.p_range_tec,
            )
        )
        time.sleep(3)    
    
client.disconnect()
client.loop_stop()