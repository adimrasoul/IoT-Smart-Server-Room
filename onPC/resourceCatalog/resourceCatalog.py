# resource catalog web service: exposing the data to others by GET; the web page can update it by POST

import cherrypy
import json

class resourceCatalog(object):
    exposed = True
    def __init__(self):
        # reading the file
        try:
            file = open("initialData.json", "r")
            self.jsonString = file.read()
            file.close()
        except:
            raise KeyError("* resourceCatalog: ERROR IN READING initialData.json *")
        self.jsonDic = json.loads(self.jsonString)
    def GET(self, *uri, **params):
        # item will contain the requeste information
        item = uri[0]
        if(item in self.jsonDic):
            result = self.jsonDic[item]
            requestedData = json.dumps(result)
            return requestedData
        elif(item == "all"):
            return self.jsonString
        else:
            return "* Nothing founded: MAKE SURE THAT YOU ARE SENDING THE RIGHT VALUE IN THE URL *"
    def POST(self, *uri, **params):
        # initial data in the resource catalog
        iniData = self.jsonDic
        # data to insert/modifiy
        data = cherrypy.request.body.read()
        newData = json.loads(data)
        # item will contain the requeste information
        item = uri[0]
        # updating the initial file by using the data coming from the web page
        if (item in iniData):
            key = list(newData.keys())[0]
            if key == 'thresholds':
                iniData[item]['thresholds']['minHum'] = newData['thresholds']['minHum']
                iniData[item]['thresholds']['minTemp'] = newData['thresholds']['minTemp']
                iniData[item]['thresholds']['maxTemp'] = newData['thresholds']['maxTemp']
                iniData[item]['thresholds']['maxHum'] = newData['thresholds']['maxHum']
            elif key == 'thingspeak':
                iniData[item]['thingspeak']['readApiKey'] = newData['thingspeak']['readApiKey']
                iniData[item]['thingspeak']['writeApiKey'] = newData['thingspeak']['writeApiKey']
                iniData[item]['thingspeak']['channelId'] = newData['thingspeak']['channelId']
                iniData[item]['thingspeak']['wsPort'] = newData['thingspeak']['wsPort']
                iniData[item]['thingspeak']['mqttBroker'] = newData['thingspeak']['mqttBroker']
                iniData[item]['thingspeak']['mqttPort'] = newData['thingspeak']['mqttPort']
            elif key == 'topic':
                iniData[item]['topic']['acTopic'] = newData['topic']['acTopic']
                iniData[item]['topic']['dhtTopic'] = newData['topic']['dhtTopic']
                iniData[item]['topic']['acOrder'] = newData['topic']['acOrder']
                iniData[item]['topic']['motionTopic'] = newData['topic']['motionTopic']
            elif key == 'broker':
                iniData['broker']['ip'] = newData['broker']['ip']
                iniData['broker']['port'] = newData['broker']['port']
            elif key == 'telegram':
                iniData['telegram']['port'] = newData['telegram']['port']
                iniData['telegram']['chatId'] = newData['telegram']['chatId']
            elif key == 'dataToRest':
                iniData['realTimeData']['ip'] = newData['realTimeData']['ip']
                iniData['realTimeData']['port'] = newData['realTimeData']['port']
        else:
            # creation of a new room by the user: inserting the new room to the json file
            key = list(newData.keys())[0]
            temporaryJson = {}
            if key == 'thresholds':
                temporaryJson["thresholds"] = {"minHum": newData['thresholds']['minHum'], "minTemp": newData['thresholds']['minTemp'], "maxTemp": newData['thresholds']['maxTemp'], "maxHum": newData['thresholds']['maxHum']}
            if key == 'thingspeak':
                temporaryJson["thingspeak"] = {"readApiKey": newData['thingspeak']['readApiKey'], "writeApiKey": newData['thingspeak']['writeApiKey'], "channelId": newData['thingspeak']['channelId'], "wsPort": newData['thingspeak']['wsPort'], "mqttBroker": newData['thingspeak']['mqttBroker'], "mqttPort": newData['thingspeak']['mqttPort']}
            if key == 'topic':
                temporaryJson["topic"] = {"acTopic": newData['topic']['acTopic'], "dhtTopic": newData['topic']['dhtTopic'], "acOrder": newData['topic']['acOrder'], "motionTopic": newData['topic']['motionTopic']}
            iniData[item] = temporaryJson
            # updating the json file
        try:
            temp = open("initialData.json", "w")
            json.dump(iniData, temp)
            return "UPDATED"
        except Exception as e:
            print ("* Error:",e)
            return "Problem in updating file *"

if __name__ == '__main__':
    # read the config file to set the url and the port on which expose the web service
    file = open("configFile.json", "r")
    jsonString = file.read()
    file.close()
    data = json.loads(jsonString)
    ip = data["resourceCatalog"]["ip"]
    port = data["resourceCatalog"]["port"]
    # configuration for the web service
    conf = { '/': { 'request.dispatch': cherrypy.dispatch.MethodDispatcher(), 'tools.sessions.on': True } }
    cherrypy.tree.mount(resourceCatalog(), '/', conf)
    cherrypy.config.update({"server.socket_host": str(ip), "server.socket_port": int(port)})
    cherrypy.engine.start()
    cherrypy.engine.block()