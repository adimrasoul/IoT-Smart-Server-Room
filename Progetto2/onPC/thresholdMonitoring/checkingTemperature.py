# checking if the temperature real time data are inside the given threshold

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
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
    def checkThresholds(self,receivedInfo):
        try:
            # sending the request to the resource catalog to get the threshold values for the specified room
            respond = requests.get(sens.urlResource + "/" + sens.roomId)
            jsonFormat = json.loads(respond.text)
        except :
            print("* CheckingTemperature: ERROR IN CONNECTING TO THE SERVER FOR READING INITIAL DATA *")
        self.acOrder = jsonFormat["topic"]["acOrder"]
        self.maxTemp = jsonFormat["thresholds"]["maxTemp"]
        # check the current values with the thresholds
        temperature = float(receivedInfo['temperature'])
        if (temperature > float(self.maxTemp)):
            #set the publisher message for turning on the A/C
            self.order = "turnOn"
            try:
                self.orderMsg = json.dumps({"subject": "acOrder", "roomId": self.roomId, "order": str(self.order)})
            except:
                print("* CheckingTemperature: ERROR IN SENDING TURN ON ORDER *")
        else:
            # set the publisher message for turning off the A/C
            self.order = "turnOff"
            try:
                self.orderMsg = json.dumps({"subject": "acOrder", "roomId": self.roomId, "order": str(self.order)})
            except:
                print("* CheckingTemperature: ERROR IN SENDING TURN OFF ORDER *")
    def on_connect(self, client, userdata, flags, rc):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print('CONNACK received with code: ' + str(rc))
        print("at time: " + str(currentTime))
    def on_publish(self, client, userdata, mid):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Published Message")
        print("at time: " + str(currentTime))
        print("--------------------------------------------------------------------")
    def on_subscribe(self, client, userdata, mid, granted_qos):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Subscribed at time: " + str(currentTime))
    def on_message(self, client, userdata, msg):
        messageBody = str(msg.payload.decode("utf-8"))
        getTime = datetime.datetime.now()
        currentTime =  getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("message received: ", messageBody)
        print("at time: " + str(currentTime))
        print("--------------------------------------------------------------------")
        receivedInfo = json.loads(messageBody)
        subject = receivedInfo["subject"]
        if (subject == "temp_hum_data"):
            self.checkThresholds(receivedInfo)
            self.publishOrder()
        else:
            pass
    def publishOrder(self):
        try:
            print("Sending: ", self.orderMsg)
            self.client.publish(self.acOrder, str(self.orderMsg))#, qos=1)
        except:
            raise KeyError("* CheckingTemperature: ERROR IN PUBLISHING THE DATA *")
    def clientStart(self,ip,port,topic):
        try:
            self.client.connect(str(ip), int(port))
            self.client.subscribe(str(topic), qos=1)
            self.client.loop_start()
        except:
            print("* CheckingTemperature: ERROR IN CONNECTING TO THE BROKER *")

if __name__ == '__main__':
    # reading the config file
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* CheckingTemperature: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    # retrieving the roomId and the resource catalog url from the config file
    resourceCatalogIp = configJson["resourceCatalog"]["url"]
    roomId = configJson["resourceCatalog"]["roomId"]
    # creating an MQTT client
    client = mqtt.Client()
    try:
        respond = requests.get(resourceCatalogIp + "/all")
        jsonFormat = json.loads(respond.text)
    except:
        print("* CheckingTemperature: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER IP *")
    ip = jsonFormat['broker']["ip"]
    port = jsonFormat['broker']["port"]
    topic = jsonFormat[roomId]['topic']['dhtTopic']
    sens = checkingThreshold(resourceCatalogIp, roomId, client)
    # sensing the data from the sensors
    sens.clientStart(ip,port,topic)
    while True:
        time.sleep(10)