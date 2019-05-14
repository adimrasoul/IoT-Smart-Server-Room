import RPi.GPIO as GPIO
import datetime
import json

"""Detection of Motion"""

class MotionDetection(object):

    def __init__(self):
        self.data = 0
        self.detection = 0

    def sensemotion(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        try:
            GPIO.setup(11, GPIO.IN)
            #GPIO.setup(3, GPIO.OUT)
            self.data = GPIO.input(11)
        except:
            print("Detecting Motion Error : ERROR IN READING THE SENSOR")

        if self.data is not None:
                if self.data == 1:
                    self.detection == 1
                elif self.data == 0:
                    self.detection == 0

            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print('Time: ',current_time,'Motion Detection: ',self.detection))
            # put all the data in a Json
            OutputJson = json.dumps({"time": current_time,"Motion Detection: ",self.detection})
            return OutputJson
        else:
            print ('ReadingMotionSensor ERROR IN SENDING JSON')
            return

if __name__ == '__main__':
    # this is for testing we use this class in the PublishTempHum class
    motion_detection_data = MotionDetection()
    while True:
        motion_detection_data.sensemotion()

