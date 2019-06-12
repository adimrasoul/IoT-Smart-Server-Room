# class that takes real time data from the web service and that expose them on ThingSpeak

import paho.mqtt.client as mqtt
import requests
import json
import time
import datetime

class dataToThingSpeak(object):
    def __init__(self,url,client,wAK,cI):
        self.url = url
        self.client = client
        self.t = time.time()
        self.payload = ''
        self.writeApiKey = wAK
        self.channelId = cI
        # create the topic string
        self.topic = str("channels/" + self.channelId + "/publish/" + self.writeApiKey)
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print('CONNACK received with code: ' + str(rc))
        print("at time: " + str(currentTime))
    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Subscribed at time: " + str(currentTime))
    @classmethod
    def on_publish(cls, client, userdata, mid):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Published Message")
        print("at time: " + str(currentTime))
        print("--------------------------------------------------------------------")
    @classmethod
    def on_message(self, client, userdata, msg):
        messageBody = str(msg.payload.decode("utf-8"))
        getTime = datetime.datetime.now()
        currentTime =  getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("message received: ", messageBody)
        print("at time: " + str(currentTime))
        print("--------------------------------------------------------------------")
        receivedInfo = json.loads(messageBody)
        sens.pub(receivedInfo)
    @classmethod
    def pub(self,receivedInfo):
        print('inside pub')
        subject = receivedInfo["subject"]
        # building the payload string
        if (subject == "temp_hum_data"):
            temperature = receivedInfo["temperature"]
            humidity = receivedInfo["humidity"]
            sens.payload += str("&field1=" + str(temperature) + "&field2=" + str(humidity))
        elif (subject == "Ac_Status"):
            acStatus = receivedInfo["Status"]
            if (acStatus == "ON"):
                result = 1
            else:
                result = 0
            sens.payload += str("&field3=" + str(result))
        elif (subject == "dehumStatus"):
            dehum = receivedInfo["Status"]
            if (dehum == "ON"):
                resultDeh = 1
            else:
                resultDeh = 0
            sens.payload += str("&field6=" + str(resultDeh))
        elif (subject == "smoke"):
            smoke = receivedInfo["value"]
            sens.payload += str("&field5=" + str(smoke))
        elif (subject == "motion_data"):
            motion = receivedInfo["Motion_Detection"]
            sens.payload += str("&field4=" + str(motion))
        print("To thingspeak: ", sens.payload)
    @classmethod
    def pubTS(self):
        # print(sens.topic)
        # print(sens.payload)
        try:
            sens.client.publish(sens.topic, sens.payload)
        except:
            print("* ThingSpeak: ERROR IN PUBLISHING TO THINGSPEAK *")
        sens.payload = ''

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
    client.on_connect = dataToThingSpeak.on_connect
    client.on_publish = dataToThingSpeak.on_publish
    client.connect(brokerIp,mqttPort,wsPort) #####
    client.loop_start()
    # MQTT client to receive real time data
    clientEclipse = mqtt.Client()
    clientEclipse.on_message = dataToThingSpeak.on_message
    clientEclipse.on_connect = dataToThingSpeak.on_connect
    clientEclipse.on_subscribe = dataToThingSpeak.on_subscribe
    # create an object from dataToThingSpeak
    sens = dataToThingSpeak(url, client, writeApiKey,channelId)
    try:
        clientEclipse.connect(brokerEclipse, int(brokerEclipsePort))
        clientEclipse.subscribe('dataCenter/#')
        clientEclipse.loop_start()
    except:
        print("* ThingSpeak: PROBLEM IN CONNECTING TO THE BROKER *")
    while True:
        time.sleep(16)
        sens.pubTS()
