from pigpio_dht import DHT22
import RPi.GPIO as GPIO
import time
import os
import pigpio

# this connects to the pigpio daemon which must be started first
pi = pigpio.pi()

os.system("sudo pigpiod")

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
        sensor = DHT22(17)
        result = sensor.read()
        timeStamp = time.ctime()
        resultHumidity = result.get('humidity')
        resultValidation = result.get('valid')
        if resultValidation == False:
            time.sleep (5) #If sensor is not meausuring properly, then program sleeps for 2 sec
        else: 
            if resultHumidity < 80:
                if resultHumidity < 50 and relayStatus == True:
                    waitXSeconds(0)
                    print('Very low humidity or atomizer is broken', result, timeStamp)
                else:
                    relayStatus = relayON(27, relayStatus)
                    waitXSeconds(0)
                    print('Low humidity', result, timeStamp)
            elif resultHumidity > 85:
                waitXSeconds(0)
                relayOFF(27)
                print('High humidity', result, timeStamp)
            elif 80 <= resultHumidity <= 85:
                print("Perfect Humidity", result, timeStamp)
            else:
                pass
except KeyboardInterrupt:
    print('cancelled by the user')
except AttributeError as err:
    print("Too many simultaneous connections", err)
finally:
    GPIO.cleanup()