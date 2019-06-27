import RPi.GPIO as GPIO
import time
from AC_Status_Publisher import PublishAcStatus
from DEHUM_Status_Publisher import PublishDEHUMStatus

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class LEDControl(object):
    # turning on and off the LED

    def __init__(self, url, roomId,source):

        if source is "AC":
            self.LedPin = 18
        elif source is "DEHUM":
            self.LedPin = 23

        # create an object from PublishDEHUMStatus class
        self.publishAC = PublishAcStatus(url, roomId)
        self.publishDEHUM = PublishDEHUMStatus(url, roomId)
        self.publishDEHUM.load()
        self.publishAC.load()

    def setup(self):
        try:
            GPIO.setwarnings(False)
            # set the GPIO modes to BCM numbering
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.LedPin, GPIO.OUT)  # initial=GPIO.HIGH

        except:
            print("LED_Control : ERROR IN SETUP THE LED")

    # Turn on
    def LED_ON(self):
        try:
            GPIO.output(self.LedPin, True)
            print("LED_Control: lED is ON")
        except Exception:
            print("LED_Control : problem in Turning the LED on")
        try:
            if self.LedPin == 18:
                print("LED_Control: The message 'ON' is publishing by AC_Status_Publisher")
                self.publishAC.stop()
                self.publishAC.publish_data("ON")
                self.publishAC.start()

            elif self.LedPin == 23:
                print("LED_Control: The message 'ON' is publishing by DEHUM_Status_Publisher")
                self.publishDEHUM.stop()
                self.publishDEHUM.publish_data("ON")
                self.publishDEHUM.start()

        except:
            print("LED_Control : Problem in publishing the 'LED_ON' ")
        return

    # Turn off
    def LED_OFF(self):
        try:
            GPIO.output(self.LedPin, False)
            print("LED_Control : LED is OFF")
        except:
            print("LED_Control : problem in Turning the LED off")
        try:
            if self.LedPin == 18:
                print("LED_Control: The message 'OFF' is publishing by AC_Status_Publisher")
                self.publishAC.stop()
                self.publishAC.publish_data("OFF")
                self.publishAC.start()

            elif self.LedPin == 23:
                print("LED_Control : The message 'OFF' is publishing by DEHUM_Status_Publisher")
                self.publishDEHUM.stop()
                self.publishDEHUM.publish_data("OFF")
                self.publishDEHUM.start()

        except:
            print("LED_Control : Problem in publishing the 'LED_OFF' ")
        return

    # define a destroy function for clean up everything after the script finished

    def destroy(self):
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

