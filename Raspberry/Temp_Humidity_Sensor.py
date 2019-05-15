import Adafruit_DHT
import datetime
import json


"Reading Data of Temperature and Humidity"

class DHT11_Reader(object):

    def __init__(self):

        self.humidity = 0
        self.temperature = 0

    def sensorData(self):

        try:
            self.humidity, self.temperature = Adafruit_DHT.read_retry(11, 27)
            "Reading Data of sensor DHT11 on PIN 27 of Raspberry"
        except:
            print("ReadingDHT: ERROR IN READING THE SENSOR")
        if self.humidity is not None and self.temperature is not None:
            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print('Time: ',current_time,'Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(self.temperature, self.humidity))
            "put all the data in a Json"
            OutputJson = json.dumps({"temperature": self.temperature, "humidity": self.humidity ,"time":current_time})

            return OutputJson
        else:
            print('ReadingDHT: ERROR IN SENDING JSON')
        return


if __name__ == '__main__':
    "this is for testing we use this class in the PublishTempHum class"
    data_of_DHT = DHT11_Reader()
    while True:
        data_of_DHT.sensorData()
