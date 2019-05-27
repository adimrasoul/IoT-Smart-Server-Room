import RPi.GPIO as GPIO
import time
#from PublishAcStatus import PublishAcStatus

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)


class LEDControl(object):
    # "turning on and off the LED"""

    def __init__(self, source):

        if source is "AC":
            pinNum = 18
        elif source is "DEHUM":
            pinNum = 23

        self.LedPin =pinNum
        # create an object from PublishAcStatus class
        # self.publish = PublishAcStatus(url, roomId)

    # setup function for some setup---custom function

    def setup(self):
        try:
            GPIO.setwarnings(False)
            # set the gpio modes to BCM numbering
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.LedPin, GPIO.OUT)  # initial=GPIO.HIGH
        except:
            print("LEDControl: ERROR IN SETUP THE LED")

    # Turn on
    def LED_ON(self):
        try:
            # self.publish.load()
            # self.publish.stop()
            GPIO.output(self.LedPin, True)
            print("lED is ON")
        except:
            print("problem in Turning the A.C on")

        # GPIO.output(self.LedPin, GPIO.LOW)
        # self.publish.publish_data("It is ON")
        # self.publish.start()
        return

    # Turn off
    def LED_OFF(self):
        try:
            # self.publish.load()
            # self.publish.stop()
            GPIO.output(self.LedPin, False)
            print("LED is OFF")
        except:
            print("problem in Turning the A.C off")
        # self.publish.publish_data("It is OFF")
        # self.publish.start()
        return

    # define a destroy function for clean up everything after the script finished
    def destroy(self):
        # turn off relay
        # GPIO.output(self.LedPin, GPIO.HIGH)
        # release resource
        GPIO.cleanup()
        return


if __name__ == '__main__':
    # this main part is for testing, this class will be used in the SubscribeAcOrder
    #pinNo = 18
    try:
        controling_LED = LEDControl()
        controling_LED.setup()
        while True:

            # disconnect
            controling_LED.LED_OFF()
            time.sleep(10)
            # connect
            controling_LED.LED_ON()
            time.sleep(10)
    except KeyboardInterrupt:
        controling_LED.destroy()


