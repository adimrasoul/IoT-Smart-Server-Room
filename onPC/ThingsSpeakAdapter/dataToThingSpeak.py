# class that takes real time data from the web service and that expose them on ThingSpeak

import paho.mqtt.client as mqtt
import requests
import json
import time

class PublishDataTS(object):
    payload = "null"
    topic = "null"
    def __init__(self,url,client):
        self.url = url
        self.client = client
    def setThingSpeakVariables(self):
        # request the thingspeak variables related the roomId, from the resource catalog
        try:
            respond = requests.get(self.url)
        except:
            print ("* ThingSpeak: ERROR IN CONNECTING TO THE SERVER FOR READING THINGSPEAKCONNECTIONINFO.JSON *")
            return
        json_format = json.loads(respond.text)
        self.writeApiKey = json_format["thingspeak"]["writeApiKey"]
        self.channelId = json_format["thingspeak"]["channelId"]
        # create the topic string
        self.topic = str("channels/" + self.channelId + "/publish/" + self.writeApiKey)
        print("ThingSpesk: THINGSPEAK VARIABLES ARE READY")
        return
    def sendingData(self, message):
        temperature = message['temp']
        humidity = message["hum"]
        status = message["acStatus"]
        if (status == "ON"):
            result = 1
        else:
            result = 0
        motion = message["motion"]
        dehum = message["dehumStatus"]
        smoke = message["smoke"]
        print("To thingspeak: ", temperature, humidity, status, motion, dehum, smoke)
        # build the payload string
        payload = str("&field1=" + str(temperature) + "&field2=" + str(humidity) + "&field3=" + str(result) + "&field4=" + str(motion) + "&field5=" + str(smoke) + "&field6=" + str(dehum))
        # attempt to publish this data to the topic
        try:
            self.client.publish(self.topic, payload)
        except:
            print("* ThingSpeak: ERROR IN PUBLISHING THE HUM AND TEMP TO THINGSPEAK *")
        return

    
if __name__ == '__main__':
    # from config file it reads the resource catalog url and the roomId that it should listen to its publishers
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* SubscribeDataTS: ERROR IN READING CONFIG FILE *")
    # reading from the local file the url of the resource catalog and the roomId we are interested in
    configJson = json.loads(jsonString)
    resourceCatalogIP = configJson["resourceCatalog"]["url"]
    roomId = configJson["resourceCatalog"]["roomId"]
    url = resourceCatalogIP + roomId
    # reading from the resourceCatalog (Web Service) the real time data IP
    respond = requests.get(resourceCatalogIP + "realTimeData")    
    jsonFormat = json.loads(respond.text)
    realTimeDataIp = jsonFormat["ip"]
    realTimeDataPort = jsonFormat["port"]
    realTimeDataUrl = realTimeDataIp + ':'+ realTimeDataPort
    print(realTimeDataUrl)
    # creating an MQTT client to publish data on ThingSpeak
    client = mqtt.Client()
    #create an object from PublishDataTS
    sens = PublishDataTS(url, client)
    # getting all info about the room we are interested in
    respond = requests.get(resourceCatalogIP + str(roomId))
    jsonFormat = json.loads(respond.text)
    # 'mqtt.thingspeak.com' - broker used to publish data on ThingSpeak
    brokerIp = jsonFormat["thingspeak"]["mqttBroker"] 
    wsPort = int(jsonFormat["thingspeak"]["wsPort"])
    mqttPort = int(jsonFormat["thingspeak"]["mqttPort"])
    # connecting to the broker
    client.connect(brokerIp,mqttPort,wsPort)
    client.loop_start()
    # setting ThingSpeak variables 
    sens.setThingSpeakVariables()
    while True:
        try:
            # reading the real time data for the given room
            respond = requests.get('http://' + realTimeDataUrl + "/" + str(roomId) + "/all")
            RTDjsonFormat = json.loads(respond.text)
            print("SubscribeDataTS: BROKER VARIABLES ARE READY")
        except:
            print("* SubscribeDataTS: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS *")
        try:
            # function that will send data to ThingSpeak
            sens.sendingData(RTDjsonFormat)
        except:
            print ("* SubscribeDataTS: PROBLEM IN CONNECTING TO THE BROKER *")
        time.sleep(30) 
