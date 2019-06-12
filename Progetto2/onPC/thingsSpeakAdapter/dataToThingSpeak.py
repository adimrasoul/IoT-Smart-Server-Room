# class that takes real time data from the web service and that expose them on ThingSpeak

import paho.mqtt.client as mqtt
import requests
import json
import time
import datetime

class dataToThingSpeak(object):
    def __init__(self,url,client,wAK,cI,client2):
        self.url = url
        self.client = client
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_connect = self.on_connect
        self.clientEclipse = client2
        self.clientEclipse.on_message = self.on_message
        self.clientEclipse.on_subscribe = self.on_subscribe
        self.clientEclipse.on_connect = self.on_connect
        self.t = time.time()
        self.payload = ''
        self.writeApiKey = wAK
        self.channelId = cI
        # create the topic string
        self.topic = str("channels/" + self.channelId + "/publish/" + self.writeApiKey)
    def on_connect(self, client, userdata, flags, rc):
        # get the current time
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print('CONNACK received with code: ' + str(rc))
        print("at time: " + str(currentTime))
    def on_subscribe(self, client, userdata, mid, granted_qos):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Subscribed at time: " + str(currentTime))
    def on_publish(self, client, userdata, mid):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Published Message")
        print("at time: " + str(currentTime))
        print("--------------------------------------------------------------------")
    def on_message(self, client, userdata, msg):
        messageBody = str(msg.payload.decode("utf-8"))
        getTime = datetime.datetime.now()
        currentTime =  getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("message received: ", messageBody)
        print("at time: " + str(currentTime))
        print("--------------------------------------------------------------------")
        receivedInfo = json.loads(messageBody)
        self.pub(receivedInfo)
    def pub(self, receivedInfo):
        subject = receivedInfo["subject"]
        # building the payload string
        if (subject == "temp_hum_data"):
            temperature = receivedInfo["temperature"]
            humidity = receivedInfo["humidity"]
            self.payload += str("&field1=" + str(temperature) + "&field2=" + str(humidity))
        elif (subject == "Ac_Status"):
            acStatus = receivedInfo["Status"]
            if (acStatus == "ON"):
                result = 1
            else:
                result = 0
            self.payload += str("&field3=" + str(result))
        elif (subject == "dehumStatus"):
            dehum = receivedInfo["Status"]
            if (dehum == "ON"):
                resultDeh = 1
            else:
                resultDeh = 0
            self.payload += str("&field6=" + str(resultDeh))
        elif (subject == "smoke"):
            smoke = receivedInfo["value"]
            self.payload += str("&field5=" + str(smoke))
        elif (subject == "motion_data"):
            motion = receivedInfo["Motion_Detection"]
            self.payload += str("&field4=" + str(motion))
        print("To thingspeak: ", self.payload)
    def pubTS(self):
        try:
            self.client.publish(self.topic, self.payload)
        except:
            print("* dataToThingSpeak: ERROR IN PUBLISHING TO THINGSPEAK *")
        self.payload = ''
    def clientConnect(self,brokerIp,mqttPort,wsPort):
        try:
            self.client.connect(brokerIp,mqttPort,wsPort)
            self.client.loop_start()
        except:
            raise KeyError("* dataToThingSpeak: ERROR IN CONNECTING TO THINGSPEAK BROKER *")
    def clientEclipseConnect(self,bI,bP,t):
        try:
            self.clientEclipse.connect(bI,bP)
            self.clientEclipse.subscribe(t)
            self.clientEclipse.loop_start()
        except:
            raise KeyError("* dataToThingSpeak: ERROR IN CONNECTING TO THINGSPEAK BROKER *")


if __name__ == '__main__':
    # from config file it reads the resource catalog url and the roomId that it should listen to its publishers
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* ThingSpeak: ERROR IN READING CONFIG FILE *")
    # reading from the local file the url of the resource catalog and the roomId we are interested in
    configJson = json.loads(jsonString)
    resourceCatalogIP = configJson["resourceCatalog"]["url"]
    roomId = configJson["resourceCatalog"]["roomId"]
    t = configJson["resourceCatalog"]["wildcard"]
    url = resourceCatalogIP + roomId
    try:
        # getting all info about the room we are interested in
        respond = requests.get(resourceCatalogIP + 'all')
        jsonFormat = json.loads(respond.text)
    except:
        raise KeyError(" * dataToThingSpeak: ERROR IN READING INFO FORM THE RESOURCE CATALOG *")
    brokerEclipse = jsonFormat['broker']['ip']
    brokerEclipsePort = jsonFormat['broker']['port']
    # 'mqtt.thingspeak.com' - broker used to publish data on ThingSpeak
    brokerIp = jsonFormat[roomId]["thingspeak"]["mqttBroker"] 
    wsPort = int(jsonFormat[roomId]["thingspeak"]["wsPort"])
    mqttPort = int(jsonFormat[roomId]["thingspeak"]["mqttPort"])
    writeApiKey = jsonFormat[roomId]["thingspeak"]["writeApiKey"] 
    channelId = jsonFormat[roomId]["thingspeak"]["channelId"] 
    # MQTT client that sends data to ThingSpeak
    client = mqtt.Client()
    #client.on_connect = dataToThingSpeak.on_connect
    #client.on_publish = dataToThingSpeak.on_publish
    # MQTT client to receive real time data
    clientEclipse = mqtt.Client()
    # create an object from dataToThingSpeak
    sens = dataToThingSpeak(url, client, writeApiKey,channelId,clientEclipse)
    sens.clientConnect(brokerIp,mqttPort,wsPort)
    sens.clientEclipseConnect(brokerEclipse,int(brokerEclipsePort),t)
    while True:
        time.sleep(16)
        sens.pubTS()
