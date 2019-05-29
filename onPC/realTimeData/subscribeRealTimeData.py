# MQTT client that will subscribe to real time data sent on the broker from the Raspberry
# and that will write the received data into a .json file

import datetime
import paho.mqtt.client as mqtt
import requests
import json

class subscribeData(object):
    def __init__(self, client):
        self.client = client
        # assigning callbacks
        client.on_subscribe = self.on_subscribe
        client.on_message = self.on_message
    # defining callbacks
    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Subscribed at time: " + str(currentTime))
    @classmethod
    def on_message(self, client, userdata, msg):
        messageBody = str(msg.payload.decode("utf-8"))
        getTime = datetime.datetime.now()
        currentTime =  getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("message received: ", messageBody)
        print("at time: " + str(currentTime))
        print("--------------------------------------------------------------------")
        # reading the file with real time data
        try:
            file = open("realTimeData.json", "r")
            jsonString = file.read()
            file.close()
        except:
            raise KeyError("* SubscribeData: ERROR IN READING JSON FILE RELATED TO REAL TIME DATA *")
        receivedInfo = json.loads(messageBody)
        actualInfoOnFile = json.loads(jsonString)
        rommId = receivedInfo["roomId"]
        subject = receivedInfo["subject"]
        # if the received info are about an existing room, updating data
        if (rommId in actualInfoOnFile):
            if (subject == "temp_hum_data"):
                actualInfoOnFile[rommId]["temp"] = receivedInfo["temperature"]
                actualInfoOnFile[rommId]["hum"] = receivedInfo["humidity"]
            elif (subject == "Ac_Status"):
                actualInfoOnFile[rommId]["acStatus"] = receivedInfo["Status"]
            elif (subject == "dehumStatus"):
                actualInfoOnFile[rommId]["dehumStatus"] = receivedInfo["Status"]
            elif (subject == "smoke"):
                actualInfoOnFile[rommId]["smoke"] = receivedInfo["value"]
            elif (subject == "motion_data"):
                actualInfoOnFile[rommId]["motion"] = receivedInfo["Motion_Detection"]
        # if the received info are not about an existing room, creating new room inside the data
        else:
            if (subject == "temp_hum_data"):
                temporaryJson = {}
                temporaryJson["temp"] = receivedInfo["temperature"]
                temporaryJson["hum"] = receivedInfo["humidity"]
                temporaryJson["acStatus"] = "OFF"
                temporaryJson["dehumSatus"] = '0'
                temporaryJson["motion"] = "0"
                temporaryJson["smoke"] = "0"
                actualInfoOnFile[rommId] = temporaryJson
            elif (subject == "Ac_Status"):
                temporaryJson = {}
                temporaryJson["temp"] = 0
                temporaryJson["hum"] = 0
                temporaryJson["acStatus"] = receivedInfo["status"]
                temporaryJson["dehumSatus"] = '0'
                temporaryJson["motion"] = "0"
                temporaryJson["smoke"] = "0"
                actualInfoOnFile[rommId] = temporaryJson
            elif (subject == "dehumStatus"):
                temporaryJson = {}
                temporaryJson["temp"] = 0
                temporaryJson["hum"] = 0
                temporaryJson["acStatus"] = "OFF"
                temporaryJson["dehumSatus"] = receivedInfo["dehumStatus"]
                temporaryJson["motion"] = "0"
                temporaryJson["smoke"] = "0"
                actualInfoOnFile[rommId] = temporaryJson
            elif (subject == "motion_data"):
                temporaryJson = {}
                temporaryJson["temp"] = 0
                temporaryJson["hum"] = 0
                temporaryJson["acStatus"] = "OFF"
                temporaryJson["dehumSatus"] = '0'
                temporaryJson["motion"] = receivedInfo["motion"]
                temporaryJson["smoke"] = "0"
                actualInfoOnFile[rommId] = temporaryJson
            elif (subject == "smoke"):
                temporaryJson = {}
                temporaryJson["temp"] = 0
                temporaryJson["hum"] = 0
                temporaryJson["acStatus"] = "OFF"
                temporaryJson["dehumSatus"] = '0'
                temporaryJson["motion"] = "0"
                temporaryJson["smoke"] = receivedInfo["value"]
                actualInfoOnFile[rommId] = temporaryJson
        # writing the new data into the file
        try:
            jsonDataFile = open("realTimeData.json", 'w')
            json.dump(actualInfoOnFile, jsonDataFile)
            jsonDataFile.close()
        except:
            raise KeyError("* SubscribeData: ERROR IN WRITING THE JSON FILE *")

if __name__ == '__main__':
    # reading the resource catalog url from the config file
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* SubscribeData: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    url = configJson["resourceCatalog"]["url"]
    topic = configJson["resourceCatalog"]["wildcard"]
    client = mqtt.Client()
    sens = subscribeData(client)
    while True:
        # sending the request to the resource catalog to set the broker ip
        try:
            respond = requests.get(url + "/broker")
            jsonFormat = json.loads(respond.text)
            brokerIP = jsonFormat["ip"]
            brokerPort = jsonFormat["port"]
            print("SubscribeData: BROKER VARIABLES ARE READY")
        except:
            print("* SubscribeData: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS *")
        # connecting to the broker and subscribing to the topic
        try:
            client.connect(brokerIP, int(brokerPort))
            client.subscribe(str(topic), qos=1)
            client.loop_forever()
        except:
            print("* SubscribeData: PROBLEM IN CONNECTING TO BROKER *")
