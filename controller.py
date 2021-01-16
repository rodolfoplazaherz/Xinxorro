import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import os
import csv

MUSHROOM_TYPE = ""
TENT_LENGHT_M = 0.6
TENT_WIDTH_M = 0.6
TENT_HEIGHT_M = 1.6
TENT_VOLUME_M3 = TENT_LENGHT_M * TENT_WIDTH_M * TENT_HEIGHT_M
FAN_CAPACITY_M3_PER_HOUR = 100
FAN_CAPACITY_M3_PER_MINUTE = FAN_CAPACITY_M3_PER_HOUR/60
AIR_EXCHANGES_PER_HOUR = 9
AIR_EXCHANGE_PERIOD_MINUTES = 60/AIR_EXCHANGES_PER_HOUR
AIR_EXCHANGE_DURATION_MINUTES = TENT_VOLUME_M3/FAN_CAPACITY_M3_PER_MINUTE


relayStatus = False


def gpioSetup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.OUT)
    GPIO.output(27, GPIO.LOW)


def relayON(gpioNumber):
    GPIO.output(gpioNumber, GPIO.LOW)
    return True


def relayOFF(gpioNumber):
    GPIO.output(gpioNumber, GPIO.HIGH)
    return False


def waitXSeconds(n):
    time.sleep(n)


try:
    initTime = time.time()
    gpioSetup()
    relayStatus = False
    with open('historicalData.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        while True:
            time.sleep(2)
            sensor = Adafruit_DHT.DHT22
            timeStamp = time.time()
            resultHumidity, resultTemperature = Adafruit_DHT.read_retry(
                sensor, 17)
            resultHumidity = round(resultHumidity, 2)
            resultTemperature = round(resultTemperature, 2)
            writer.writerow([resultHumidity, resultTemperature, timeStamp])
            if resultHumidity == None or resultTemperature == None:
                # If sensor is not meausuring properly, then program sleeps for 2 sec
                waitXSeconds(2)
            else:
                print("rh:{}, °C:{}, time:{}".format(
                    resultHumidity, resultTemperature, timeStamp))
                if resultHumidity < 80:
                    if resultHumidity < 50 and relayStatus == True:
                        waitXSeconds(0)
                        print('Very low humidity or atomizer is broken')
                    else:
                        relayStatus = relayON(27)
                        waitXSeconds(0)
                        print('Low humidity')
                elif resultHumidity > 80:
                    waitXSeconds(0)
                    relayStatus = relayOFF(27)
                    print('High humidity, turning OFF the relay')
                # elif 80 <= resultHumidity <= 85:
                #     relayStatus = relayOFF(27)
                #     print("Perfect Humidity, relayOFF")
                else:
                    pass
except KeyboardInterrupt:
    print('cancelled by the user, cleaning')
finally:
    GPIO.cleanup()
