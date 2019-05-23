import json
import time
import requests
import telepot

class telegramBot(object):
    def __init__(self,url,port):
        self.url = url
    def setWebServiceVariables(self):
        # reading real time data ip and port
        try:
            respond = requests.get(self.url+"realTimeData")
        except:
            print ("TelegramBot: ERROR IN CONNECTING TO THE SERVER FOR GETTING RESTFUL WEB SERVICE URL")
        # set the url to ask for the real time data
        json_format = json.loads(respond.text)
        self.restURL = json_format["ip"]
        self.port = json_format["port"]
        print ("TelegramBot: RESTFUL ARE READY")
    def handler(self, msg):
        # getting the information from the received message
        chat_id = msg['chat']['id']
        command = msg['text']
        self.setWebServiceVariables()
        bot.sendMessage(chat_id, self.sendResult(command))
    def sendResult(self,command):
        # sending back the result by asking the data related to the room_id received by the telegrom
        print('trying to send back the result')
        try:
            # sending the request to the mqtt to web service
            result = requests.get("http://"+self.restURL + ":" + self.port + "/"+command+"/all")#.content
            jsonformat = json.loads(result.text)
            temp=jsonformat['temp']
            hum=jsonformat['hum']
            staus=jsonformat['acStatus']
            dehum = jsonformat['dehumStatus']
            motion = jsonformat['motion']
            if int(motion) == 1:
                mot = "DETECTED"
            else:
                mot = "NOT DETECTED"
            smoke = jsonformat['smoke']
            if int(dehum) == 0:
                deh = "OFF"
            else:
                deh = "ON"
            outputString = 'Temperature: '+ str(temp) + '; humidity: ' + str(hum) +"; acStatus: "+str(staus) +"; motion:" + str(mot) + "; smoke:" + str(smoke) + "; dehumidificator:" + str(deh)
            #print(outputString)
        except:
                return "Please enter the correct room id\nex: room_1"

        return str(outputString)

if __name__ == '__main__':
    # read the config file to find the resource catalog url
    try:
        file = open("configFile.json", "r")
        json_string = file.read()
        file.close()
    except:
        raise KeyError("* DataWithRest: ERROR IN READING CONFIG FILE *")
    config_json = json.loads(json_string)
    url = config_json["resourceCatalog"]["url"]
    # sending request to the resource catolog to get the telegram bot port
    try:
        respond = requests.get(url+"telegram")
        json_format = json.loads(respond.text)
        port = json_format["port"]
        telegram_bot = telegramBot(url,port)
    except:
        print ("ERROR IN CONNECTING TO SERVER FOR GETTING TELEGROM BOT PORT")
    # set the port and start the loop
    try:
        def handle(msg):
            telegram_bot.handler(msg)
        bot = telepot.Bot(port)
        bot.message_loop(handle)
        print('Listening')
    except:
        print("TelegramBot: ERROR IN CONNECTING TO THE TELEGRAM BOT")
    while 1:
        time.sleep(10)