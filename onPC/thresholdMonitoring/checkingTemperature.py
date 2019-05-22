# checking if the real time data are inside the given threshold
# temperature

import requests
import json
import time
import datetime
import paho.mqtt.client as mqtt

class checkingThreshold(object):
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
            self.acOrder = jsonFormat["topic"]["acOrder"]
            self.maxTemp = jsonFormat["thresholds"]["maxTemp"]
            self.minTemp = jsonFormat["thresholds"]["minTemp"]
        except :
            print("* CheckingThreshold: ERROR IN CONNECTING TO THE SERVER FOR READING initial_data.JSON *")
        return
    def gettingTempHum(self):
        # sending request to the MQTT To WebService to get the current value for temperature and humidity
        try:
            self.temperature = requests.get("http://" + self.restURL + ":" + self.port + "/" + self.roomId + "/temp").content
            print("real time data", self.temperature)
        except:
            print("* CheckingThreshold: ERROR IN GETTING DATA FROM WEB SERVICE *")
        return
    def checkThresholds(self):
        # check the current values with the thresholds
        temperature = float(self.temperature)
        if (temperature > float(self.maxTemp)):
            #set the publisher message for turning on the A/C
            self.order = "turnOn"
            try:
                self.orderMsg = json.dumps({"subject": "acOrder", "roomId": self.roomId, "order": str(self.order)})
            except:
                print("* CheckingThreshold: ERROR IN SENDING TURN ON ORDER *")
        else:
            # set the publisher message for turning off the A/C
            self.order = "turnOff"
            try:
                self.orderMsg = json.dumps({"subject": "acOrder", "roomId": self.roomId, "order": str(self.order)})
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
            print(self.acOrder)
            self.client.publish(self.acOrder, str(self.orderMsg))#, qos=1)
        except:
            getTime = datetime.datetime.now()
            currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
            print("* PublishAcStatus: ERROR IN PUBLISHING THE DATA *")
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
    # create a class checkingThreshold
    sens = checkingThreshold(resourceCatalogIp, roomId, client)
    # sensing the data from the sensors
    while True:
        sens.loadFile()
        sens.gettingTempHum()
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
            client.on_connect = checkingThreshold.on_connect
            client.on_publish = checkingThreshold.on_publish
            client.connect(str(ip), int(port))
            client.loop_start()
        except:
            print("* PublishData: ERROR IN CONNECTING TO THE BROKER *")
        sens.publish_order()
        time.sleep(10)