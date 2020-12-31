from pigpio_dht import DHT22
import RPi.GPIO as GPIO
import time
import os

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
    print("Waiting {} seconds".format(n))
    time.sleep(n)

try:
    gpioSetup()
    relayStatus = False
    while True:
        sensor = DHT22(17)
        result = sensor.read()
        timeStamp = time.ctime()
        resultHumidity = result.get('humidity')
        resultValidation = result.get('valid')
        if resultValidation == False:
            time.sleep (2) #If sensor is not meausuring properly, then program sleeps for 2 sec
        else: 
            if resultHumidity < 80:
                if resultHumidity < 50 and relayStatus == True:
                    waitXSeconds(2)
                    print('case3: atomizer is broken')
                    print(result)
                else:
                    relayStatus = relayON(27, relayStatus)
                    print(relayStatus)
                    waitXSeconds(2)
                    print('case1: low humidity')
                    print(result, timeStamp)
            elif resultHumidity > 85:
                waitXSeconds(2)
                relayOFF(27)
                print('case2: high humidity')
                print(result)
            else:
                print("Something is wrong")
except KeyboardInterrupt:
    print('cancelled by the user')
finally:
    GPIO.cleanup()