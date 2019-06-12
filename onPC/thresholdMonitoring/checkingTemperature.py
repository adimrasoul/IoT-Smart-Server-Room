# checking if the temperature real time data are inside the given threshold

import requests
import json
import time
import datetime
import paho.mqtt.client as mqtt

class checkingThreshold(object):
    def __init__(self, url, roomId, client,tT):
        self.urlResource = url
        self.roomId = roomId
        self.client = client
        self.tTopic = tT
    @classmethod
    def checkThresholds(self,receivedInfo):
        try:
            # sending the request to the resource catalog to get the threshold values for the specified room
            respond = requests.get(sens.urlResource + "/" + sens.roomId)
            jsonFormat = json.loads(respond.text)
            self.acOrder = jsonFormat["topic"]["acOrder"]
            self.maxTemp = jsonFormat["thresholds"]["maxTemp"]
        except :
            print("* CheckingTemperature: ERROR IN CONNECTING TO THE SERVER FOR READING INITIAL DATA *")
        # check the current values with the thresholds
        # receivedInfo = json.loads(messageBody)
        temperature = float(receivedInfo['temperature'])
        if (temperature > float(self.maxTemp)):
            #set the publisher message for turning on the A/C
            self.order = "turnOn"
            try:
                self.orderMsg = json.dumps({"subject": "acOrder", "roomId": sens.roomId, "order": str(self.order)})
            except:
                print("* CheckingTemperature: ERROR IN SENDING TURN ON ORDER *")
        else:
            # set the publisher message for turning off the A/C
            self.order = "turnOff"
            try:
                self.orderMsg = json.dumps({"subject": "acOrder", "roomId": sens.roomId, "order": str(self.order)})
            except:
                print("* CheckingTemperature: ERROR IN SENDING TURN OFF ORDER *")
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print('CONNACK received with code: ' + str(rc))
        print("at time: " + str(currentTime))
    @classmethod
    def on_publish(cls, client, userdata, mid):
        print(sens.orderMsg)
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Published Message")
        print("at time: " + str(currentTime))
        print("--------------------------------------------------------------------")
    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Subscribed at time: " + str(currentTime))
    @classmethod
    def publishOrder(self):
        # publishing AC order
        try:
            print(self.acOrder, self.orderMsg, sens.tTopic)
            sens.client.publish(self.acOrder, str(self.orderMsg))#, qos=1)
            if (self.order == 'turnOn'):
                sens.client.publish(sens.tTopic, str('on'))#, qos=1)
            else:
                pass
        except:
            raise KeyError("* CheckingTemperature: ERROR IN PUBLISHING THE DATA *")
    @classmethod
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
            checkingThreshold.checkThresholds(receivedInfo)
            checkingThreshold.publishOrder()
        else:
            pass

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
    client.on_connect = checkingThreshold.on_connect
    client.on_publish = checkingThreshold.on_publish
    client.on_subscribe = checkingThreshold.on_subscribe
    client.on_message = checkingThreshold.on_message
    # create a class checkingThreshold
    try:
        respond = requests.get(resourceCatalogIp + "/all")
        jsonFormat = json.loads(respond.text)
        ip = jsonFormat['broker']["ip"]
        port = jsonFormat['broker']["port"]
        topic = jsonFormat[roomId]['topic']['dhtTopic']
        tTopic = jsonFormat[roomId]['topic']['thresholdTopic']
    except:
        print("* CheckingTemperature: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER IP *")
    sens = checkingThreshold(resourceCatalogIp, roomId, client,tTopic)
    # sensing the data from the sensors
    try:
        client.connect(str(ip), int(port))
        client.subscribe(str(topic), qos=1)
        client.loop_start()
    except:
        print("* CheckingTemperature: ERROR IN CONNECTING TO THE BROKER *")
    while True:
        time.sleep(10)