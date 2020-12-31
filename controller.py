import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import os

relayStatus = False

def gpioSetup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.OUT)
    GPIO.output(27,GPIO.LOW)

def relayON(gpioNumber, relayStatus):
    GPIO.output(gpioNumber, GPIO.HIGH)
    relayStatus = True
    return relayStatus

def relayOFF(gpioNumber):
    GPIO.output(gpioNumber, GPIO.LOW)
    relayStatus = False
    return relayStatus

def waitXSeconds(n):
    time.sleep(n)

try:
    gpioSetup()
    relayStatus = False
    while True:
        time.sleep(2)
        sensor = Adafruit_DHT.DHT22
        timeStamp = time.ctime()
        resultHumidity, resultTemperature = Adafruit_DHT.read_retry(sensor, 17)
        if resultHumidity == None or resultTemperature == None:
            time.sleep (5) #If sensor is not meausuring properly, then program sleeps for 2 sec
        else: 
            print(resultHumidity, resultTemperature, timeStamp)
            if resultHumidity < 80:
                if resultHumidity < 50 and relayStatus == True:
                    waitXSeconds(0)
                    print('Very low humidity or atomizer is broken', timeStamp)
                else:
                    relayStatus = relayON(27, relayStatus)
                    waitXSeconds(0)
                    print('Low humidity', timeStamp)
            elif resultHumidity > 85:
                waitXSeconds(0)
                relayOFF(27)
                print('High humidity', timeStamp)
            elif 80 <= resultHumidity <= 85:
                print("Perfect Humidity", timeStamp)
            else:
                pass
except KeyboardInterrupt:
    print('cancelled by the user')
finally:
    GPIO.cleanup()