import RPi.GPIO as GPIO
import time
#from PublishDEHUMStatus import PublishDEHUMStatus
from AC_Status_Publisher import PublishAcStatus
from DEHUM_Status_Publisher import PublishDEHUMStatus
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#GPIO.setup(18, GPIO.OUT)


class LEDControl(object):
    # "turning on and off the LED"""

    def __init__(self, url, roomId,source):

        if source is "AC":
            self.LedPin = 18
        elif source is "DEHUM":
            self.LedPin = 23

        # create an object from PublishDEHUMStatus class
        self.publishAC = PublishAcStatus(url, roomId)
        self.publishDEHUM = PublishDEHUMStatus(url, roomId)
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
            GPIO.output(self.LedPin, True)
            print("lED is ON")
        except Exception:
            print("problem in Turning the A.C on")
        try:
            if self.LedPin == 18:
                self.publishAC.load()
                self.publishAC.stop()
                self.publishAC.publish_data("ON")
                self.publishAC.start()
                print("LED_Comtrol: The message 'ON' is sent by AC_Status_Publisher")
            elif self.LedPin == 23:
                self.publishDEHUM.load()
                self.publishDEHUM.stop()
                self.publishDEHUM.publish_data("ON")
                self.publishDEHUM.start()
                print("LED_Comtrol: The message 'ON' is sent by DEHUM_Status_Publisher")
        except:
            print("Problem in publishing the 'LED_is_ON' ")
        return

    # Turn off
    def LED_OFF(self):
        try:
            GPIO.output(self.LedPin, False)
            print("LED is OFF")
        except:
            print("problem in Turning the A.C off")
        try:
            if self.LedPin == 18:
                self.publishAC.load()
                self.publishAC.stop()
                self.publishAC.publish_data("OFF")
                self.publishAC.start()
                print("LED_Comtrol: The message 'OFF' is sent by AC_Status_Publisher")
            elif self.LedPin == 23:
                self.publishDEHUM.load()
                self.publishDEHUM.stop()
                self.publishDEHUM.publish_data("OFF")
                self.publishDEHUM.start()
                print("LED_Comtrol: The message 'OFF' is sent by DEHUM_Status_Publisher")
        except:
            print("Problem in publishing the 'LED_is_ON' ")
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
        controling_LED = LEDControl("AC")
        controling_LED2 = LEDControl("DEHUM")
        controling_LED.setup()
        controling_LED2.setup()
        while True:

            # disconnect
            controling_LED.LED_OFF()
            controling_LED2.LED_OFF()
            time.sleep(10)
            # connect
            controling_LED.LED_ON()
            controling_LED2.LED_ON()
            time.sleep(10)
    except KeyboardInterrupt:
        controling_LED.destroy()
        controling_LED2.destroy()

