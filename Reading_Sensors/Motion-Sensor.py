import RPi.GPIO as GPIO
import datetime


while True:

    if i==0:
        print("No Intruder",i)
        GPIO.output(3,0)
        time.sleep(0.1)
    elif i==1:
        print("Intruder Detected",i)
        GPIO.output(3,1)
        time.sleep(0.1)



""""Detection of Motion"""

class Motion_Detection(object):

    def __init__(self):
        self.data = 0
        self.detection = 0

    def senseMotion(self):

        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(11, GPIO.IN)
            GPIO.setup(3, GPIO.OUT)
            self.data = GPIO.input(11)
        except:
            print("Detecting Motion Error : ERROR IN READING THE SENSOR")

        while True:

            if self.data is not None:
                if self.data == 1:
                    self.detection == 1
                elif self.data == 0:
                    self.detection == 0

            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print('Time: ',current_time,'Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(self.temperature, self.humidity))
            "put all the data in a Json"
            OutputJson = json.dumps({"temperature": self.temperature, "humidity": self.humidity,"time":current_time})

            return OutputJson
        else:
            print('ReadingDHT: ERROR IN SENDING JSON')
        return