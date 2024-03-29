from Motion_Sensor import MotionDetection
import paho.mqtt.client as mqttc
import time
import datetime
import requests
import json

"""publishing the data of Motion Sensor"""


class PublishData(object):

    def __init__(self, url, sensor_t_h,roomId, client):
        self.url = url
        self.sensor_t_h = sensor_t_h
        self.client = client
        self.roomId=roomId

    def load_topics(self):
        # sending request to the resource catalog to get the topics related to the room id
        try:
            self.respond = requests.get(self.url)
            json_format = json.loads(self.respond.text)
            self.motion_Topic = json_format["topic"]["motionTopic"]
            print("Motion_Publisher:: BROKER VARIABLES ARE READY")
        except:
            print("Motion_Publisher: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        # get the current time
        get_time = datetime.datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print ('CONN ACK received with code: ' + str(rc))
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

    def publish_sensor_data(self):
        # This function will publish the data related to temperature and humidity
        try:
            inputJsonFromTHSensor = self.sensor_t_h.sensemotion()
            inputData = json.loads(inputJsonFromTHSensor)
            motionDetection = inputData["Motion_Detection"]
            outputJson=json.dumps({"subject":"motion_data", "roomId":self.roomId, "Motion_Detection": motionDetection})
            msg_info = client.publish(self.motion_Topic, str(outputJson), qos=1)
            print("\n Motion_Publisher: Message is published.")
            return ("HELLO", json_format)
        except:
            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print("Motion_Publisher: ERROR IN PUBLISHING DATA RELATED TO THE SENSORS")
            print ("at time: " + str(current_time))


if __name__ == '__main__':

    try:
        # reading the config file to set the resource catalog url and the room id
        file = open("config_file.json", "r")
        json_string = file.read()
        file.close()
    except:
        raise KeyError("***** Motion_Publisher: ERROR IN READING CONFIG FILE *****")

    config_json = json.loads(json_string)
    resourceCatalogIP = config_json["reSourceCatalog"]["url"]
    roomId = config_json["reSourceCatalog"]["roomId"]
    url = resourceCatalogIP + roomId
    try:
        # create an object from ReadingDHT class
        sensor_data = MotionDetection()
    except:
        print("Motion_Publisher: ERROR IN GETTING DATA FROM SENSOR ")

    client = mqttc.Client()
    sens = PublishData(url, sensor_data,roomId, client)
    sens.load_topics()
    try:
        # requesting the broker info from resource catalog
        respond = requests.get(resourceCatalogIP+"broker")
        json_format = json.loads(respond.text)
        broker_ip = json_format["ip"]
        port = json_format["port"]
    except:
        print("Motion_Publisher: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER IP")

    try:
        client.on_connect = PublishData.on_connect
        client.on_publish = PublishData.on_publish
        client.connect(broker_ip, int(port))
        client.loop_start()
    except:
        print("Motion_Publisher: ERROR IN CONNECTING TO THE BROKER")

    while True:
        sens.publish_sensor_data()
        time.sleep(15)
