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

HUMIDIFIER_GPIO = 0
VENTILATOR_GPIO = 27
SENSOR_DHT22_GPIO = 17


relayStatus = False


def gpioSetup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.OUT)


def relayON(gpioNumber):
    GPIO.output(gpioNumber, GPIO.HIGH)
    return True


def relayOFF(gpioNumber):
    GPIO.output(gpioNumber, GPIO.LOW)
    return False


def waitXSeconds(n):
    time.sleep(n)


def ventilatorController():
    pass


def sensorController(relayStatus):
    with open('historicalData.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        while True:
            sensor = Adafruit_DHT.DHT22
            timeStamp = time.time()
            resultHumidity, resultTemperature = Adafruit_DHT.read_retry(
                sensor, SENSOR_DHT22_GPIO)
            resultHumidity = round(resultHumidity, 2)
            resultTemperature = round(resultTemperature, 2)
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
                        relayStatus = relayON(HUMIDIFIER_GPIO)
                        waitXSeconds(0)
                        print('Low humidity')
                elif resultHumidity > 80:
                    waitXSeconds(0)
                    relayStatus = relayOFF(HUMIDIFIER_GPIO)
                    print('High humidity, turning OFF the relay')
                else:
                    pass
            writer.writerow(
                [resultHumidity, resultTemperature, timeStamp, relayStatus])


def main():
    try:
        gpioSetup()
        relayStatus = False
        sensorController(relayStatus)
    except KeyboardInterrupt:
        print("Cancelled by the user, cleaning")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
