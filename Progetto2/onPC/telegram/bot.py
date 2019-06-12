# telegram bot

import time
import telepot
import json
import requests
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class botto(object):
    def __init__(self, chatId, t, i, p,rU):
        self.chatId = chatId
        self.token = t
        self.realDataIp = i
        self.port = p
        self.flag1 = False
        self.flag2 = False
        self.flag3 = False
        self.flag4 = False
        self.flag5 = False
        self.resourceUrl = rU
        self.bot = telepot.Bot(self.token)
        # creating the buttons
        self.keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Info about room1', callback_data='room1')],[InlineKeyboardButton(text="Info about room2", callback_data='room2')],[InlineKeyboardButton(text="Modify thresholds about a room", callback_data='roomT')]])
        # sending a message with buttons
        self.bot.sendMessage(self.chatId, 'Welcome to the data center!', reply_markup = self.keyboard)
        # associating the button with the callbacks
        MessageLoop(self.bot, {'chat': self.on_chat_message,'callback_query': self.on_callback_query}).run_as_thread()
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if self.flag1 == True:
            self.roomId = msg['text']
            self.flag1 = False
            self.flag2 = True
            self.bot.sendMessage(chat_id, 'Insert the minimum value of humidity:')
        elif self.flag2 == True:
            self.minHum = msg['text']
            self.flag2 = False
            self.flag3 = True
            self.bot.sendMessage(chat_id, 'Insert the minimum value of temperature:')
        elif self.flag3 == True:
            self.minTemp = msg['text']
            self.flag3 = False
            self.flag4 = True
            self.bot.sendMessage(chat_id, 'Insert the maximum value of humidity:')
        elif self.flag4 == True:
            self.maxHum = msg['text']
            self.flag4 = False
            self.flag5 = True
            self.bot.sendMessage(chat_id, 'Insert the maximum value of temperature:')
        elif self.flag5 == True:
            self.maxTemp = msg['text']
            self.flag5 = False
            js = {'thresholds': {'minHum': self.minHum, 'minTemp': self.minTemp, 'maxHum': self.maxHum, 'maxTemp': self.maxTemp}}
            j = json.dumps(js)
            try:
                response = requests.post(self.resourceUrl + self.roomId, data=j)
                # self.bot.sendMessage(self.chatId, 'Thresholds updated succesfully!')
                self.bot.sendMessage(chat_id, 'Thresholds updated succesfully!')
            except:
                raise KeyError('* botto: ERROR IN UPDAITNG THE RESOURCE CATALOG *')
            # sending a message with buttons
            # self.bot.sendMessage(self.chatId, 'Data center', reply_markup = self.keyboard)
            self.bot.sendMessage(chat_id, 'Data center', reply_markup = self.keyboard)
        else:
            # sending a message with buttons
            # self.bot.sendMessage(self.chatId, 'Data center', reply_markup=self.keyboard)
            self.bot.sendMessage(chat_id, 'Data center', reply_markup=self.keyboard)
    def on_callback_query(self, msg):
        # data about the pressed button
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('callback:', query_id, from_id, query_data)
        # checking what button is been pressed
        if ((query_data == 'room1') | (query_data == 'room2')):
            try:
                url = str('http://' + str(self.realDataIp) + ':' + str(self.port) + '/' + query_data + '/all')
                respons = requests.get(url)
                jsonFormat = json.loads(respons.text)
            except:
                raise KeyError("* telegramBot: ERROR IN GETTING REAL TIME DATA *")
            t = str(jsonFormat['temp'])
            h = str(jsonFormat['hum'])
            aS = str(jsonFormat['acStatus'])
            dS = str(jsonFormat['dehumStatus'])
            # m = jsonFormat['motion']
            # s = jsonFormat['smoke']
            s = '- temperature: ' + t + '°C; \n- humidity: ' + h + '%; \n- AC status: ' + aS + '; \n- dehumidifier status: ' + dS + '.'
            #self.bot.sendMessage(self.chatId, s)
            self.bot.sendMessage(from_id, s)
            #self.bot.sendMessage(self.chatId, 'data center', reply_markup = self.keyboard)
            self.bot.sendMessage(from_id, 'data center', reply_markup = self.keyboard)
        else:
            # self.bot.sendMessage(self.chatId, 'Insert, in order, the following values separateed by a space.')
            # self.bot.sendMessage(self.chatId, 'room id (i.e. room1 or room2), minimum humidity, minimum temperature, maximum humidity, maximum temperature')
            self.flag1 = True
            #self.bot.sendMessage(self.chatId, 'Insert room id (room1 or room2):')
            self.bot.sendMessage(from_id, 'Insert room id (room1 or room2):')

if __name__ == '__main__':
    # reading the resource catalog url from the configuration  file
    try:
        file = open("configFile.json", "r")
        jsonString = file.read()
        file.close()
    except:
        raise KeyError("* telegramBot: ERROR IN READING CONFIG FILE *")
    configJson = json.loads(jsonString)
    resUrl = configJson["resourceCatalog"]["url"]
    # sending a request to the resource catalog to get the url on which the data will be published on
    respond = requests.get(resUrl + "all")
    jsonFormat = json.loads(respond.text)
    ip = jsonFormat["realTimeData"]["ip"]
    port = jsonFormat["realTimeData"]["port"]
    chatId = jsonFormat["telegram"]["chatId"]
    token = jsonFormat["telegram"]["port"]
    b = botto(chatId,token,ip,port,resUrl)
    while 1:
        time.sleep(10)
    