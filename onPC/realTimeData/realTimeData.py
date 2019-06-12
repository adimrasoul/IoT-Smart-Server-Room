# MQTT client that will subscribe to real time data sent on the broker from the Raspberry
# and that will write the received data into a .json file, with these it
# expose the data into a web service

import datetime
import paho.mqtt.client as mqtt
import requests
import json
import cherrypy

class subscribeData(object):
    # needed to expose the GET method
    exposed = True
    def __init__(self, client):
        self.client = client
    def connBrok(self,bI,bP):
        try:
            self.client.connect(bI, int(bP))
            self.client.subscribe(str(topic), qos=1)
            self.client.loop_forever()
        except:
            print("* realTimeData: PROBLEM IN CONNECTING TO BROKER *")        
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
            raise KeyError("* realTimeData: ERROR IN READING JSON FILE RELATED TO REAL TIME DATA *")
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
            elif (subject == "motion_data"):
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
            raise KeyError("* realTimeData: ERROR IN WRITING THE JSON FILE *")
    def GET(self, *uri, **params):
        # reading the real time data file when it receives the request
        try:
            file = open("realTimeData.json", "r")
            jsonString = file.read()
            item = uri[0]
            file.close()
        except:
            raise KeyError("* realTimeData: ERROR IN READING JSON FILE RELATED TO DATA *")
        results = json.loads(jsonString)
        # if the first parameter of the url is all, returns all data
        if (item == "all"):
            return jsonString
        # otherwise, it returns the data of a specific room
        if (item in results):
            if (uri[1] == 'temp'):
                return str(results[item]['temp'])
            elif (uri[1] == 'hum'):
                return str(results[item]['hum'])
            elif (uri[1] == 'ac'):
                return str(results[item]['acStatus'])
            elif (uri[1] == 'dehum'):
                return str(results[item]['dehumStatus'])
            elif (uri[1] == 'smoke'):
                return str(results[item]['smoke'])
            elif (uri[1] == 'mot'):
                return str(results[item]['motion'])
            elif (uri[1] == 'all'):
                return str(json.dumps(results[item]))
        else:
            return "Nothing found, check the input again"

if __name__ == '__main__':
    # reading the resource catalog url from the config file
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* realTimeData: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    url = configJson["resourceCatalog"]["url"]
    topic = configJson["resourceCatalog"]["wildcard"]
    client = mqtt.Client()
    client.on_subscribe = subscribeData.on_subscribe
    client.on_message = subscribeData.on_message
    sens = subscribeData(client)
    # sending the request to the resource catalog to set the broker ip
    try:
        respond = requests.get(url + "/all")
        jsonFormat = json.loads(respond.text)
        brokerIp = jsonFormat["broker"]["ip"]
        brokerPort = jsonFormat["broker"]["port"]
        ip = jsonFormat["realTimeData"]["ip"]
        port = jsonFormat["realTimeData"]["port"]
    except:
        print("* realTimeData: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS *")
    # configuration for the web service
    conf = { '/': { 'request.dispatch': cherrypy.dispatch.MethodDispatcher(), 'tools.sessions.on': True } }
    # building the web service
    cherrypy.tree.mount(subscribeData(client), '/', conf)
    cherrypy.config.update({"server.socket_host": str(ip), "server.socket_port": int(port)})
    cherrypy.engine.start()
    sens.connBrok(brokerIp,brokerPort)
    cherrypy.engine.block()
    