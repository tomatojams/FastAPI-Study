from paho.mqtt import client as mqtt_client
import random
import time

broker = 'localhost'
port = 1883
topic = "test/sample"
client_id = f"publish-{random.randint(0, 1000)}"


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client,messages):
    result = client.publish(topic, messages)
    if result == mqtt_client.MQTT_ERR_SUCCESS:
        print(f"Sent `{messages}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

client = connect_mqtt()
