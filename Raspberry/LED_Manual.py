import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class LEDControl(object):
    # "turning on and off the LED"""

    def __init__(self, url, roomId,source):

        if source is "AC":
            self.LedPin = 18
        elif source is "DEHUM":
            self.LedPin = 23

    def setup(self):
        try:
            GPIO.setwarnings(False)
            # set the gpio modes to BCM numbering
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.LedPin, GPIO.OUT)  # initial=GPIO.HIGH

        except:
            print("LED_Manual: ERROR IN SETUP THE LED")

    # Turn on
    def LED_ON(self):
        try:
            GPIO.output(self.LedPin, True)
            print("lED is ON")
        except Exception:
            print("LED_Manual : problem in Turning the A.C on")
        return

    # Turn off
    def LED_OFF(self):
        try:
            GPIO.output(self.LedPin, False)
            print("LED_Manual : LED is OFF")
        except:
            print("LED_Manual : problem in Turning the A.C off")
        return

    # define a destroy function for clean up everything after the script finished
    def destroy(self):

        GPIO.cleanup()

        return


if __name__ == '__main__':
    # this main part is for testing, this class will be used in the SubscribeAcOrder
    try:
        controling_LED = LEDControl("http://172.20.10.15:8080/","room_1","AC")
        controling_LED2 = LEDControl("http://172.20.10.15:8080/","room_1","DEHUM")
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

