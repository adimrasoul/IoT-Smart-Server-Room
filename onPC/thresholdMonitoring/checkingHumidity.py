# checking if the real time data are inside the given threshold
# humidity

import requests
import json
import time
import datetime
import paho.mqtt.client as mqtt

class checkingHumidity(object):
    def __init__(self, url, roomId, client):
        self.urlResource = url
        self.roomId = roomId
        self.client = client
    def loadFile(self):
        try:
            # sending the request to the resource catalog to get the MQTT to webService url
            respond = requests.get(self.urlResource + "/realTimeData")
            jsonFormat = json.loads(respond.text)
            self.restURL = jsonFormat["ip"]
            self.port = jsonFormat["port"]
        except :
            print("* CheckingThreshold: ERROR IN CONNECTING TO THE SERVER FOR GETTING WEB SERVICE IP *")
        try:
            # sending the request to the resource catalog to get the threshold values for the specified room
            respond = requests.get(self.urlResource + "/" + self.roomId)
            jsonFormat = json.loads(respond.text)
            self.dehumOrder = jsonFormat["topic"]["dehumOrder"]
            self.maxHum = jsonFormat["thresholds"]["maxHum"]
            self.minHum = jsonFormat["thresholds"]["minHum"]
        except :
            print("* CheckingThreshold: ERROR IN CONNECTING TO THE SERVER FOR READING initial_data.JSON *")
        return
    def gettingHum(self):
        # sending request to the MQTT To WebService to get the current value for temperature and humidity
        try:
            self.humidity = requests.get("http://" + self.restURL + ":" + self.port + "/" + self.roomId + "/hum").content
            print("real time data", self.humidity)
        except:
            print("* CheckingThreshold: ERROR IN GETTING DATA FROM WEB SERVICE *")
        return
    def checkThresholds(self):
        # check the current values with the thresholds
        humidity = float(self.humidity)
        if ((humidity > float(self.maxHum)) or (humidity < float(self.minHum))):
            # set the publisher message for turning on the A/C
            self.order = "turnOn"
            try:
                self.orderMsg = json.dumps({"subject": "dehumOrder", "roomId": self.roomId, "order": str(self.order)})
            except:
                print("* CheckingThreshold: ERROR IN SENDING TURN ON ORDER *")
        else:
            # set the publisher message for turning off the A/C
            self.order = "turnOff"
            try:
                self.orderMsg = json.dumps({"subject": "dehumOrder", "roomId": self.roomId, "order": str(self.order)})
            except:
                print("* CheckingThreshold: ERROR IN SENDING TURN OFF ORDER *")
        return
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        # get the current time
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print('CONNACK received with code: ' + str(rc))
        print("at time: " + str(currentTime))
        return str(rc)
    @classmethod
    def on_publish(cls, client, userdata, mid):
        # get the current time
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Published Message")
        print("at time: " + str(currentTime))
        print("--------------------------------------------------------------------")
        return str(mid)
    def publish_order(self):
        # this function will publish the order to AC
        try:
            print(self.orderMsg)
            print(self.dehumOrder)
            self.client.publish(self.dehumOrder, str(self.orderMsg))#, qos=1)
        except:
            getTime = datetime.datetime.now()
            currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
            print("* PublishHumStatus: ERROR IN PUBLISHING THE DATA *")
            print("at time: " + str(currentTime))
        return

if __name__ == '__main__':
    # reading the config file
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* CheckingThreshold: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    # retrieving the roomId and the resource catalog url from the config file
    resourceCatalogIp = configJson["resourceCatalog"]["url"]
    roomId = configJson["resourceCatalog"]["roomId"]
    # creating an MQTT client
    client = mqtt.Client()
    # create a class checkingHumidity
    sens = checkingHumidity(resourceCatalogIp, roomId, client)
    # sensing the data from the sensors
    while True:
        sens.loadFile()
        sens.gettingHum()
        sens.checkThresholds()
        # sending request to resource catalog to get the broker ip
        try:
            respond = requests.get(resourceCatalogIp + "/broker")
            jsonFormat = json.loads(respond.text)
            ip = jsonFormat["ip"]
            port = jsonFormat["port"]
        except:
            print("* PublishData: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER IP *")
        try:
            client.on_connect = checkingHumidity.on_connect
            client.on_publish = checkingHumidity.on_publish
            client.connect(str(ip), int(port))
            client.loop_start()
        except:
            print("* PublishData: ERROR IN CONNECTING TO THE BROKER *")
        sens.publish_order()
        time.sleep(10)