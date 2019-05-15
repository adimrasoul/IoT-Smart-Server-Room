# web service that reads the real time data and expose it on the given url

import cherrypy
import json
import requests

class realTimeDataWebService(object):
    exposed = True
    def GET(self, *uri, **params):
        # reading the real time data file when it recives the request
        try:
            file = open("realTimeData.json", "r")
            jsonString = file.read()
            item = uri[0]
            file.close()
        except:
            raise KeyError("* DataWithRest: ERROR IN READING JSON FILE RELATED TO DATA *")
        results = json.loads(jsonString)
        # if the item exist inside the json file, it will return the asked data
        if (item == "all"):
            return jsonString
        if (item in results):
            if (uri[1] == 'temp'):
                return str(results[item]['temp'])
            elif (uri[1] == 'hum'):
                return str(results[item]['hum'])
            elif (uri[1] == 'ac'):
                return str(results[item]['acStatus'])
            elif (uri[1] == 'mot'):
                return str(results[item]['motion'])
            elif (uri[1] == 'all'):
                return str(json.dumps(results[item]))
        # if the item does not exist, returns a warning
        else:
            return "Nothing found, check the input again"

if __name__ == '__main__':
    # reading the reaource catalog url from the json file
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* realTimeData: ERROR IN READING CONFIG FILE *")
    # sending request to the resource catalog to ask for the MQTT to web service URL
    configJson = json.loads(jsonString)
    url = configJson["resourceCatalog"]["url"]
    respond = requests.get(url + "/realTimeData")
    jsonFormat = json.loads(respond.text)
    # set the IP and the port that the mqtt to web service should expose the data on it
    hostIP = jsonFormat["ip"]
    port = jsonFormat["port"]
    # configuration for the web service
    conf = { '/': { 'request.dispatch': cherrypy.dispatch.MethodDispatcher(), 'tools.sessions.on': True } }
    # building the web service
    cherrypy.tree.mount(realTimeDataWebService(), '/', conf)
    cherrypy.config.update({"server.socket_host": str(hostIP), "server.socket_port": int(port)})
    cherrypy.engine.start()
    cherrypy.engine.block()
