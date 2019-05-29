import paho.mqtt.client as paho
import datetime
import json
import requests


class PublishDEHUMStatus(object):

    def __init__(self,url,roomId):
        self.url = url
        self.roomId = roomId
        self.client = paho.Client()
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        # get the current time
        get_time = datetime.datetime.now()
        current_time =  get_time.strftime("%Y-%m-%d %H:%M:%S")
        print ('CONNACK received with code: ' + str(rc))
        print ("at time: " + str(current_time))
        return str(rc)

    @classmethod
    def on_publish(cls, client, userdata, mid):
        # get the current time
        get_time = datetime.datetime.now()
        current_time =  get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("mid: " + str(mid))
        print ("at time: " + str(current_time))
        print("--------------------------------------------------------------------")
        return str(mid)

    def publish_data(self,order):
        #This function will publish the order to AC
        try:
            json_format = json.dumps({'subject':'dehumStatus','roomId':self.roomId,'Status' : str(order)})
            self.client.publish(self.AC_Topic, str(json_format), qos=1)
            return ("CIAONE", json_format)
        except:
            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print ("DEHUM_Status_Publisher:ERROR IN PUBLISHING THE DATA")
            print ("at time: " + str(current_time))

    def start(self):
        self.client.loop_start();

    def stop(self):
        self.client.loop_stop();

    def load(self):
        # sending request to reaourse catalog to set hte broker ip and port
        try:
            respond = requests.get(self.url+"broker")
            json_format = json.loads(respond.text)
            Broker_IP = json_format["ip"]
            Broker_port = json_format["port"]
            print("DEHUM_Status_Publisher: BROKER VARIABLES ARE READY")
        except:
            print("DEHUM_Status_Publisher: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")

        try:
            # sending the room+id to the resource catalog to get the topic
            respond = requests.get(self.url + self.roomId)
            json_format = json.loads(respond.text)
            self.AC_Topic = json_format["topic"]["dehumTopic"]
            print("DEHUM_Status_Publisher: BROKER VARIABLES ARE READY")
        except:
            print("DEHUM_Status_Publisher: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")
        try:
            self.client.connect(Broker_IP, int(Broker_port))
        except:
            print("DEHUM_Status_Publisher:ERROR IN CONNECTING TO THE BROKER")
