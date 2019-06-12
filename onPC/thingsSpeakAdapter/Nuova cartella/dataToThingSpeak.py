# class that takes real time data from the web service and that expose them on ThingSpeak

import paho.mqtt.client as mqtt
import requests
import json
import time

class dataToThingSpeak(object):
    def __init__(self,url,client):
        self.url = url
        self.client = client
        # request the thingspeak variables related the roomId, from the resource catalog
        try:
            respond = requests.get(self.url)
        except:
            print("* ThingSpeak: ERROR IN CONNECTING TO THE SERVER FOR READING THINGSPEAKCONNECTIONINFO.JSON *")
        json_format = json.loads(respond.text)
        self.writeApiKey = json_format["thingspeak"]["writeApiKey"]
        self.channelId = json_format["thingspeak"]["channelId"]
        # create the topic string
        self.topic = str("channels/" + self.channelId + "/publish/" + self.writeApiKey)
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
        if (dehum == "ON"):
            resultDeh = 1
        else:
            resultDeh = 0
        smoke = message["smoke"]
        print("To thingspeak: ", temperature, humidity, status, motion, dehum, smoke)
        # build the payload string
        payload = str("&field1=" + str(temperature) + "&field2=" + str(humidity) + "&field3=" + str(result) + "&field4=" + str(motion) + "&field5=" + str(smoke) + "&field6=" + str(resultDeh))
        # attempt to publish this data to the topic
        try:
            self.client.publish(self.topic, payload)
        except:
            print("* ThingSpeak: ERROR IN PUBLISHING TO THINGSPEAK *")
    
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
    # reading from the resourceCatalog the real time data IP
    respond = requests.get(resourceCatalogIP + "realTimeData")    
    jsonFormat = json.loads(respond.text)
    realTimeDataIp = jsonFormat["ip"]
    realTimeDataPort = jsonFormat["port"]
    realTimeDataUrl = realTimeDataIp + ':'+ realTimeDataPort
    # creating an MQTT client to publish data on ThingSpeak
    client = mqtt.Client()
    # create an object from dataToThingSpeak
    sens = dataToThingSpeak(url, client)
    # getting all info about the room we are interested in
    respond = requests.get(resourceCatalogIP + str(roomId))
    jsonFormat = json.loads(respond.text)
    # 'mqtt.thingspeak.com' - broker used to publish data on ThingSpeak
    brokerIp = jsonFormat["thingspeak"]["mqttBroker"] 
    wsPort = int(jsonFormat["thingspeak"]["wsPort"])
    mqttPort = int(jsonFormat["thingspeak"]["mqttPort"])
    try:
        # connecting to the broker
        client.connect(brokerIp,mqttPort,wsPort)
        client.loop_start()
    except:
        print("* ThingSpeak: PROBLEM IN CONNECTING TO THE BROKER *")
    while True:
        try:
            # reading the real time data for the given room
            respond = requests.get('http://' + realTimeDataUrl + "/" + str(roomId) + "/all")
            jsonForm = json.loads(respond.text)
        except:
            print("* ThingSpeak: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS *")
        # sending data to ThingSpeak
        sens.sendingData(jsonForm)
        time.sleep(30) 
