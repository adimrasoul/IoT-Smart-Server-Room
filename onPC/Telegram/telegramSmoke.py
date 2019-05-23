# program that will check if the smoke status reveals that there is smoke

import json
import time
import requests


class telegramAlarm(object):
    def __init__(self, urlRealTime,roomId):
        self.urlRealTime = urlRealTime
        self.roomId = roomId
        # needed a first time to read the initial value of the motion sensor
        return
    def checkValue(self):
        try:
            # getting the real time data
            realTimeData = requests.get(self.urlRealTime + "/all")
            jsonFormatDue = json.loads(realTimeData.text)
        except:
            print("* telegramSmoke: ERROR IN CONNECTING TO REAL TIME DATA WEB SERVICE *")
        self.value = jsonFormatDue[self.roomId]['smoke']
        # if the previous value of the motion sensor was different from the actual, send a message
        if (int(self.value) > 80):
            sendText1 = 'https://api.telegram.org/bot' + port + '/sendMessage?chat_id=' + chatId + '&parse_mode=Markdown&text=' + 'ALERT'
            sendText2 = 'https://api.telegram.org/bot' + port + '/sendMessage?chat_id=' + chatId + '&parse_mode=Markdown&text=' + 'there is smoke'
            response = requests.get(sendText1)
            response = requests.get(sendText2)
        else:
            pass


if __name__ == '__main__':
    # reading the config file to find the resource catalog url
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* telegramSmoke: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    url = configJson["resourceCatalog"]["url"]
    roomId = configJson["resourceCatalog"]["roomId"]
    # sending a request to the resource catolog to get info on the telegram bot and the url with the real time data
    try:
        respond = requests.get(url + "all")
        jsonFormat = json.loads(respond.text)
    except:
        print("* telegramSmoke: ERROR IN CONNECTING TO RESOURCE CATALOG WEB SERVICE *")
    port = jsonFormat['telegram']["port"]
    chatId = jsonFormat['telegram']["chatId"]
    urlRealTime = 'http://' + jsonFormat['realTimeData']['ip'] + ':' + jsonFormat['realTimeData']['port']
    obj = telegramAlarm(urlRealTime,roomId)
    while True:
        obj.checkValue()
        time.sleep(20)