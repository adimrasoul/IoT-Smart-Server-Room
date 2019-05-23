# web service that reads the real time data from the .json file and expose it

import cherrypy
import json
import requests

class realTimeDataWebService(object):
    exposed = True
    def GET(self, *uri, **params):
        # reading the real time data file when it receives the request
        try:
            file = open("realTimeData.json", "r")
            jsonString = file.read()
            item = uri[0]
            file.close()
        except:
            raise KeyError("* RealTimeData: ERROR IN READING JSON FILE RELATED TO DATA *")
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
    # reading the resource catalog url from the configuration  file
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* RealTimeData: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    url = configJson["resourceCatalog"]["url"]
    # sending a request to the resource catalog to get the url on which the data will be published on
    respond = requests.get(url + "/realTimeData")
    jsonFormat = json.loads(respond.text)
    ip = jsonFormat["ip"]
    port = jsonFormat["port"]
    # configuration for the web service
    conf = { '/': { 'request.dispatch': cherrypy.dispatch.MethodDispatcher(), 'tools.sessions.on': True } }
    # building the web service
    cherrypy.tree.mount(realTimeDataWebService(), '/', conf)
    cherrypy.config.update({"server.socket_host": str(ip), "server.socket_port": int(port)})
    cherrypy.engine.start()
    cherrypy.engine.block()
