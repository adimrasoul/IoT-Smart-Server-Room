import datetime
import json
import random
import time
"Reading Data of Temperature and Humidity"

class Smoke_Detection(object):

    def __init__(self):

        self.smoke = 0

    def senseSmoke(self):
        try:
            "Generating Random number for smoke"
            self.smoke = random.randint(1, 100)
            print("Smoke_Detection : Generated smoke No. is ",self.smoke)

        except:
            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print("Smoke_Detection : Errot in Generating Value of Smoke at time: " + str(current_time))

        if self.smoke is not None :
            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            "put all the data in a Json"
            OutputJson = json.dumps({"value": str(self.smoke), "time": current_time})
            print("JSON Content: ", OutputJson)
            return OutputJson
        else:
            print(': ERROR IN SENDING JSON')
        return


if __name__ == '__main__':
    "this is for testing we use this class in the PublishTempHum class"
    smokeData = Smoke_Detection()
    while True:
        smokeData.senseSmoke()
        time.sleep(10)