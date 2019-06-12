# program that whill check if the motion status changes in time and send an alert message to Telegram Bot

import json
import time
import datetime
import requests
import paho.mqtt.client as mqtt

class telegramAlarm(object):
    def __init__(self,roomId,cl,p,cI):
        self.roomId = roomId
        self.client = cl
        self.port = p
        self.chatId = cI
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        getTime = datetime.datetime.now()
        currentTime = getTime.strftime("%Y-%m-%d %H:%M:%S")
        print('CONNACK received with code: ' + str(rc))
        print("at time: " + str(currentTime))
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
        if (messageBody == "on"):
            sendText1 = 'https://api.telegram.org/bot' + obj.port + '/sendMessage?chat_id=' + obj.chatId + '&parse_mode=Markdown&text=' + 'ALERT!'
            sendText2 = 'https://api.telegram.org/bot' + obj.port + '/sendMessage?chat_id=' + obj.chatId + '&parse_mode=Markdown&text=' + 'temperature above the thresold'
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
        raise KeyError("* telegramMotion: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    url = configJson["resourceCatalog"]["url"]
    roomId = configJson["resourceCatalog"]["roomId"]
    client = mqtt.Client()
    client.on_message = telegramAlarm.on_message
    client.on_subscribe = telegramAlarm.on_subscribe
    client.on_connect = telegramAlarm.on_connect
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
    topic = jsonFormat[roomId]["topic"]["thresholdTopic"]
    try:
        client.connect(brokerIp,int(brokerPort))
        client.subscribe(topic)
        client.loop_start()
    except:
        raise KeyError("* telegramTemp: ERROR IN CONNECTING TO THE BROKER *")
    obj = telegramAlarm(roomId,client,port,chatId)
    while True:
        time.sleep(10)