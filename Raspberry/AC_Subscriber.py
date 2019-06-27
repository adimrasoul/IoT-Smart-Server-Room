import datetime
import paho.mqtt.client as paho
import requests
import json
import time
from LED_Control import LEDControl

""" Here we subscribe the orders to AC. to Turn the AC ON or OFF"""


class SubscribeAcOrder(object):

    payload = "null"
    orders = 'null'

    def __init__(self, url, roomId, client):
        self.url =url
        self.room_Id = roomId
        self.source = "AC"
        # create an object from LEDControl class
        self.controlling_LED = LEDControl(url, roomId,self.source)
        self.client = client
        client.on_subscribe = self.on_subscribe
        client.on_message = self.on_message

    def load_topics(self):
        # Sending request to get the topic by sending the room_id to the resource catalog
        try:
            self.respond = requests.get(self.url + self.room_Id)
            json_format = json.loads(self.respond.text)
            self.AC_status = json_format["topic"]["acOrder"]
            print("AC_Subscriber : Ac TOPIC ARE READY")
        except:
            print("AC_Subscriber : ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")

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
        print("AC_Subscriber : calling order function")
        # for every message that will receive we will call the order function
        sens.order()

    def order(self):
        # Order function will check the data of payload. if it is turn on it will try to call setup and led_on function
        # LED Control file. if it is turn off vice versa. in LED Control there are some lines that will try to publish
        # the status of AC by using AC Status Publisher

        print("AC_Subscriber : order function is called")
        if self.orders == "turnOn":
            print("AC_Subscriber : Sending Turn on order to LED")

            try:
                self.controlling_LED.setup()
                self.controlling_LED.LED_ON()
            except:
                print("AC_Subscriber : ERROR IN SENDING TURN ON ORDER TO LED")

        elif self.orders == "turnOff":
            print("AC_Subscriber : Sending Turn off order to LED")
            try:
                self.controlling_LED.setup()
                self.controlling_LED.LED_OFF()
            except:
                print("AC_Subscriber : ERROR IN SENDING TURN OFF ORDER TO RELAY")


if __name__ == '__main__':
    # RUN THE SUBSCRIBE FOR GETTING THE TEMPERATURE AND HUMIDITY DATA
    try:
        # read the config file to set hte resource catalog url and the room_id
        file = open("config_file.json", "r")
        json_string = file.read()
        file.close()
    except:
        raise KeyError("***** AC_Subscriber : ERROR IN READING CONFIG FILE *****")

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
        print("AC_Subscriber:: BROKER VARIABLES ARE READY")
    except:
        print("AC_Subscriber: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")
    try:
        client.connect(Broker_IP, int(Broker_Port))
        client.subscribe(str(sens.AC_status), qos=1)
        client.loop_start()

        while True:
            time.sleep(1)
    except:

        print("AC_Subscriber: Problem in connecting to broker")




