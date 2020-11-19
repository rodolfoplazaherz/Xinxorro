from pigpio_dht import DHT22
import RPi.GPIO as GPIO
import time

relayStatus = False

def gpioSetup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.OUT)
    GPIO.output(27,GPIO.LOW)

def relayON(gpioNumber):
    GPIO.output(gpioNumber, GPIO.HIGH)
    relayStatus = True
    return relayStatus

def relayOFF(gpioNumber):
    GPIO.output(gpioNumber, GPIO.LOW)
    relayStatus = False
    return relayStatus

def waitXSeconds(n):
    for i in range (0,n):
    time.sleep(n)
    print(i)

try:
    gpioSetup()
    relayStatus = False
    while True:
        sensor = DHT22(17)
        result = sensor.read()
        resultHumidity = result.get('humidity')
        if resultHumidity < 80:
            relayON(27)
            print(relayStatus)
            waitXSeconds(10)
            print('case1')
            print(result)
        elif resultHumidity > 85:
            waitXSeconds(10)
            relayOFF(27)
            print('case2')
            print(result)
        elif resultHumidity < 50 and relayStatus == True:
            waitXSeconds(10)
            print('case3: atomizer is broken')
            print(result)
except KeyboardInterrupt:
    print('cancelled by the user')
finally:
    GPIO.cleanup()