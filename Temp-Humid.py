import RPi.GPIO as GPIO
#import DHT11
import Adafruit_DHT
import time
import datetime

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

sensor = Adafruit_DHT.DHT11
pin = 27
#humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
# read data using pin 14
while True:
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	if humidity is not None and temperature is not None:
    		print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
		time.sleep(0.5)
	else:
    		print('Failed to get reading. Try again!')
