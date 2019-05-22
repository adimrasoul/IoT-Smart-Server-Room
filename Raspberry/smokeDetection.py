import paho.mqtt.client as mqtt
import time
import datetime
import requests
import json
import random

class PublishData(object):
    def __init__(self, url, roomId, client):
        self.url = url
        self.client = client
        self.roomId = roomId
    def load_topics(self):
        # sending request to the resource catalog to get the topics related to the room id
        try:
            self.respond = requests.get(self.url)
            json_format = json.loads(self.respond.text)
            self.smokeTopic = json_format["topic"]["smokeTopic"]
            print("PublishData:: BROKER VARIABLES ARE READY")
        except:
            print("PublishData: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        # get the current time
        get_time = datetime.datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print('CONNACK received with code: ' + str(rc))
        print("at time: " + str(current_time))
        return str(rc)
    @classmethod
    def on_publish(cls, client, userdata, mid):
        # get the current time
        get_time = datetime.datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("mid: " + str(mid))
        print("at time: " + str(current_time))
        print("--------------------------------------------------------------------")
        return str(mid)
    def publishSmokeData(self):
        # This function will publish the data related to temperature and humidity
        try:
            value = random.randint(1, 100)
            jsonFormat = json.dumps({"subject": "smoke", "roomId": self.roomId, "value": str(value)})
            msgInfo = client.publish(self.smokeTopic, str(jsonFormat), qos=1)
            print("Message published:", msgInfo)
            return
        except:
            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print("PublishData: ERROR IN PUBLISHING DATA RELATED TO THE SENSORS")
            print("at time: " + str(current_time))


if __name__ == '__main__':
    try:
        # reading the config file to set the resource catalog url and the room id
        file = open("config_file.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* PublishData: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    resourceCatalogIp = configJson["resourceCatalog"]["url"]
    roomId = configJson["resourceCatalog"]["roomId"]
    url = resourceCatalogIp + roomId
    client = mqtt.Client()
    sens = PublishData(url, roomId, client)
    sens.load_topics()
    try:
        # requesting the vroker info from resource catalog
        respond = requests.get(resourceCatalogIp + "/broker")
        json_format = json.loads(respond.text)
        brokerIp = json_format["ip"]
        port = json_format["port"]
    except:
        print("PublishData: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER IP")
    try:
        client.on_connect = PublishData.on_connect
        client.on_publish = PublishData.on_publish
        client.connect(brokerIp, int(port))
        client.loop_start()
    except:
        print("PublishData: ERROR IN CONNECTING TO THE BROKER")

    while True:
        sens.publishSmokeData()
        time.sleep(30)
