# checking if the humidity real time data are inside the given threshold

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
            respond = requests.get(self.urlResource + "/" + self.roomId)
            jsonFormat = json.loads(respond.text)
        except:
            print("* CheckingHumidity: ERROR IN CONNECTING TO THE SERVER FOR READING INITIAL DATA *")
        self.dehumOrder = jsonFormat["topic"]["dehumOrder"]
        self.maxHum = jsonFormat["thresholds"]["maxHum"]
        # check the current values with the thresholds
        humidity = float(receivedInfo['humidity'])
        if (humidity > float(self.maxHum)):
            #set the publisher message for turning on the A/C
            self.order = "turnOn"
            try:
                self.orderMsg = json.dumps({"subject": "dehumOrder", "roomId": self.roomId, "order": str(self.order)})
            except:
                print("* CheckingHumidity: ERROR IN SENDING TURN ON ORDER *")
        else:
            # set the publisher message for turning off the A/C
            self.order = "turnOff"
            try:
                self.orderMsg = json.dumps({"subject": "dehumOrder", "roomId": self.roomId, "order": str(self.order)})
            except:
                print("* CheckingHumidity: ERROR IN SENDING TURN OFF ORDER *")
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
    def publishOrder(self):
        # publishing dehumidificator order
        print("Sending: ", self.orderMsg)
        try:
            self.client.publish(self.dehumOrder, str(self.orderMsg))#, qos=1)
        except:
            raise KeyError("* CheckingHumidity: ERROR IN PUBLISHING THE DATA *")
    def on_message(self, client, userdata, msg):
        messageBody = str(msg.payload.decode("utf-8"))
        getTime = datetime.datetime.now()
        currentTime =  getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("message received: ", messageBody)
        print("at time: " + str(currentTime))
        print("----------------------------------------------------------------")
        receivedInfo = json.loads(messageBody)
        subject = receivedInfo["subject"]
        if (subject == "temp_hum_data"):
            self.checkThresholds(receivedInfo)
            self.publishOrder()
        else:
            pass
    def clientStart(self,ip,port,topic):
        try:
            self.client.connect(str(ip), int(port))
            self.client.subscribe(str(topic), qos=1)
            self.client.loop_start()
        except:
            print("* CheckingHumidity: ERROR IN CONNECTING TO THE BROKER *")

if __name__ == '__main__':
    try:
        # reading the config file
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* CheckingHumidity: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    # retrieving the roomId and the resource catalog url from the config file
    resourceCatalogIp = configJson["resourceCatalog"]["url"]
    roomId = configJson["resourceCatalog"]["roomId"]
    # creating an MQTT client
    client = mqtt.Client()
    # create a class checkingThreshold
    sens = checkingThreshold(resourceCatalogIp, roomId, client)
    try:
        respond = requests.get(resourceCatalogIp + "/all")
        jsonFormat = json.loads(respond.text)
    except:
        print("* CheckingHumidity: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER IP *")
    ip = jsonFormat['broker']["ip"]
    port = jsonFormat['broker']["port"]
    topic = jsonFormat[roomId]['topic']['dhtTopic']
    sens.clientStart(ip,port,topic)
    while True:
        time.sleep(10)