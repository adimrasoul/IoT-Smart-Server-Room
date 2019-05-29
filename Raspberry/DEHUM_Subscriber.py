import datetime
import paho.mqtt.client as paho
import requests
import json
import time
from LED_Control import LEDControl

class SubscribeAcOrder(object):

    payload = "null"
    orders = 'null'

    def __init__(self, url, roomId, client):
        # this flag is for checking the current status of the A/C
        #self.flag = 0
        self.url =url
        self.room_Id = roomId
        self.source = "DEHUM"
        # create an object from LEDbyRlay class
        self.controlling_LED = LEDControl(url, roomId,self.source)
        self.client = client
        client.on_subscribe = self.on_subscribe
        client.on_message = self.on_message
    def load_topics(self):
# sending request to get the topic by sending the room_id to the resource catalog
        try:
            self.respond = requests.get(self.url + self.room_Id)
            json_format = json.loads(self.respond.text)
            self.AC_status = json_format["topic"]["dehumOrder"]
            print("SubscribeDehumOrder: Ac TOPIC ARE READY")
        except:
            print("SubscribeDehumOrder: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        get_time = datetime.datetime.now()
        current_time =  get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("Subscribed: " + str(mid) + " " + str(granted_qos))
        print ("at time: " + str(current_time))

    @classmethod
    def on_message(cls,client, userdata, msg):
        get_time = datetime.datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("message received ", str(msg.payload.decode("utf-8")))
        print ("at time: " + str(current_time))
        print("--------------------------------------------------------------------")
        message_body = str(msg.payload.decode("utf-8"))
        cls.payload = json.loads(message_body)
        print(cls.payload["order"])
        cls.orders = cls.payload["order"]

    def order(self):
        print("order function is called")
# here check the order, and apply it ine time by using the flag
        if self.orders == "turnOn":
            # and self.flag == 0
            print("Sending Turn on order")

            try:
                self.controlling_LED.setup()
                self.controlling_LED.LED_ON()
                #self.flag = 1
            except:
                print("SubscribeDehumOrder: ERROR IN SENDING TURN ON ORDER TO RELAY")

        elif self.orders == "turnOff":
             #and self.flag == 1:
            print("Sending Turn off order To Dehum LED")
            try:
                self.controlling_LED.setup()
                self.controlling_LED.LED_OFF()
                #self.flag = 0
            except:
                print("SubscribeAcOrder: ERROR IN SENDING TURN OFF ORDER TO RELAY")


if __name__ == '__main__':
    # RUN THE SUBSCRIBE FOR GETTING THE TEMPERATURE AND HUMIDITY DATA
    try:
        # read the comfig file to set hte resource catalog url and the room_id
        file = open("config_file.json", "r")
        json_string = file.read()
        file.close()
    except:
        raise KeyError("***** SubscribeAcOrder: ERROR IN READING CONFIG FILE *****")

    config_json = json.loads(json_string)
    resourceCatalogip = config_json["reSourceCatalog"]["url"]
    roomId = config_json["reSourceCatalog"]["roomId"]
    client = paho.Client()
    sens = SubscribeAcOrder(resourceCatalogip,roomId, client)

    try:
        # sending request to resource catalog to get the broker info

        sens.load_topics()
        respond = requests.get(resourceCatalogip+"broker")
        json_format = json.loads(respond.text)
        Broker_IP = json_format["ip"]
        Broker_Port = json_format["port"]
        print("SubscribeAcOrder:: BROKER VARIABLES ARE READY")
    except:
            print("SubscribeAcOrder: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")
    try:
        client.connect(Broker_IP, int(Broker_Port))
        client.loop_start()
        client.subscribe(str(sens.AC_status), qos=1)# dataCenter/room1/order


        while True:
            #client.subscribe("dataCenter/room1/#", qos=1)
            print("calling order function")
            sens.order()
            time.sleep(5)
    except:
        print("SubscribeAcOrder: Problem in connecting to broker")




