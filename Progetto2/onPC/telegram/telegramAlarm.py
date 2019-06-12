# sending an alert message to Telegram Bot if: smoke; motion; high temperature

import json
import time
import datetime
import requests
import paho.mqtt.client as mqtt

class telegramAlarm(object):
    def __init__(self,roomId,cl,port,cI):
        self.roomId = roomId
        self.client = cl
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_connect = self.on_connect
        self.port = port
        self.chatId = cI
    def on_connect(self, client, userdata, flags, rc):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print('CONNACK received with code: ' + str(rc))
        print("at time: " + str(currentTime))
    def on_subscribe(self, client, userdata, mid, granted_qos):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Subscribed at time: " + str(currentTime))
    def on_message(self, client, userdata, msg):
        messageBody = str(msg.payload.decode("utf-8"))
        getTime = datetime.datetime.now()
        currentTime =  getTime.strftime("%Y-%m-%d %H:%M:%S")
        print("message received: ", messageBody)
        print("at time: " + str(currentTime))
        print("----------------------------------------------------------------")
        receivedInfo = json.loads(messageBody)
        subject = receivedInfo["subject"]
        if (subject == "motion_data"):
            if (int(receivedInfo['Motion_Detection']) == 1):
                s = "someone inside the room"
                sendText1 = 'https://api.telegram.org/bot' + self.port + '/sendMessage?chat_id=' + self.chatId + '&parse_mode=Markdown&text=' + 'ALERT!'
                sendText2 = 'https://api.telegram.org/bot' + self.port + '/sendMessage?chat_id=' + self.chatId + '&parse_mode=Markdown&text=' + 'change in motion status'
                sendText3 = 'https://api.telegram.org/bot' + self.port + '/sendMessage?chat_id=' + self.chatId + '&parse_mode=Markdown&text=' + str(s)
                try:
                    response = requests.get(sendText1)
                    response = requests.get(sendText2)
                    response = requests.get(sendText3)
                    print("Sent motion alarm")
                except:
                    raise KeyError("* telegramAlarm: ERROR IN SENDING MOTION ALARM *")
            else:
                pass
        elif (subject == "smoke"):
            # if the smoke value is above a threshold
            if (int(receivedInfo['value']) > 80):
                sendText1 = 'https://api.telegram.org/bot' + self.port + '/sendMessage?chat_id=' + self.chatId + '&parse_mode=Markdown&text=' + 'ALERT!'
                sendText2 = 'https://api.telegram.org/bot' + self.port + '/sendMessage?chat_id=' + self.chatId + '&parse_mode=Markdown&text=' + 'smoke detected'
                try:
                    response = requests.get(sendText1)
                    response = requests.get(sendText2)
                    print("Sent smoke alarm")
                except:
                    raise KeyError("* telegramAlarm: ERROR IN SENDING SMOKE ALARM *")
            else:
                pass
        elif (subject == "acOrder"):
            if (receivedInfo['order']):
                sendText1 = 'https://api.telegram.org/bot' + self.port + '/sendMessage?chat_id=' + self.chatId + '&parse_mode=Markdown&text=' + 'ALERT!'
                sendText2 = 'https://api.telegram.org/bot' + self.port + '/sendMessage?chat_id=' + self.chatId + '&parse_mode=Markdown&text=' + 'temperature above the thresold'
                try:
                    response = requests.get(sendText1)
                    response = requests.get(sendText2)
                    print("Sent temperature alarm")
                except:
                    raise KeyError("* telegramAlarm: ERROR IN SENDING TEMPERATURE ALARM *")
            else:
                pass
        else:
            pass
    def clientConnect(self,brokerIp,brokerPort,topic):
        try:
            self.client.connect(brokerIp,int(brokerPort))
            self.client.subscribe(topic)
            self.client.loop_start()
        except:
            raise KeyError("* telegramMotion: ERROR IN CONNECTING TO THE BROKER *")
        
if __name__ == '__main__':
    # reading the config file to find the resource catalog url
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* telegramMotion: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    url = configJson["resourceCatalog"]["url"]
    roomId = configJson["resourceCatalog"]["roomId"]
    t = configJson["resourceCatalog"]["wildcard"]
    client = mqtt.Client()
    # sending a request to the resource catalog to get info on the telegram bot and the url with the real time data
    try:
        respond = requests.get(url+"all")
        jsonFormat = json.loads(respond.text)
    except:
        print("* telegramMotion: ERROR IN CONNECTING TO RESOURCE CATALOG WEB SERVICE *")
    port = jsonFormat['telegram']["port"]
    chatId = jsonFormat['telegram']["chatId"]
    brokerIp = jsonFormat["broker"]["ip"]
    brokerPort = jsonFormat["broker"]["port"]
    obj = telegramAlarm(roomId,client,port,chatId)
    obj.clientConnect(brokerIp,brokerPort,t)
    while True:
        time.sleep(20)