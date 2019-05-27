from Smoke_Sensor import Smoke_Detection
import paho.mqtt.client as mqttc
import time
import datetime
import requests
import json


class PublishData(object):

    def __init__(self, url, sensor_s, roomId, client):
        self.url = url
        self.sensor_s = sensor_s
        self.client = client
        self.roomId=roomId

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
        print ('CONN ACK received with code: ' + str(rc))
        print ("at time: " + str(current_time))
        return str(rc)

    @classmethod
    def on_publish(cls, client, userdata, mid):
        # get the current time
        get_time = datetime.datetime.now()
        current_time =  get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("mid: " + str(mid))
        print ("at time: " + str(current_time))
        print("--------------------------------------------------------------------")
        return str(mid)

    def publishSmokeData(self):
        #This function will publish the data related to temperature and humidity
        try:
            inputJsonFromSmokeSensor = self.sensor_s.senseSmoke()
            inputData = json.loads(inputJsonFromSmokeSensor)
            smokeValue = inputData["value"]
            time1 = inputData["time"]

            jsonFormat = json.dumps({"subject": "smoke", "roomId": self.roomId, "value":smokeValue,"time":time1 })
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
        json_string = file.read()
        file.close()
    except:
        raise KeyError("***** PublishData: ERROR IN READING CONFIG FILE *****")

    config_json = json.loads(json_string)
    resourceCatalogIP = config_json["reSourceCatalog"]["url"]
    roomId = config_json["reSourceCatalog"]["roomId"]
    url = resourceCatalogIP + roomId

    try:
        # create an object from ReadingDHT class
        sensor_data = Smoke_Detection()
    except:
        print("PublishData: ERROR IN GETTING DATA FROM SENSOR ")

    client = mqttc.Client()
    sens = PublishData(url, sensor_data,roomId, client)

    while True:
        sens.load_topics()
        try:
            #requesting the vroker info from resource catalog
            respond = requests.get(resourceCatalogIP+"/broker")
            json_format = json.loads(respond.text)
            broker_ip = json_format["Broker_IP"]
            port = json_format["Broker_port"]
        except:
            print("PublishData: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER IP")

        try:
            client.on_connect = PublishData.on_connect
            client.on_publish = PublishData.on_publish
            client.connect(broker_ip, int(port))
            client.loop_start()
        except:
            print("PublishData: ERROR IN CONNECTING TO THE BROKER")

        while True:
            sens.load_topics()
            sens.publishSmokeData()
            time.sleep(30)