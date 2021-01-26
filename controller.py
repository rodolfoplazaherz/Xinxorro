import os
import csv
import time
import datetime
import threading
import Adafruit_DHT
import RPi.GPIO as GPIO
from ConfigurationHandler import loadConfigData

Config = loadConfigData()

TENT_VOLUME_M3 = Config.get("TENT_LENGHT_M") * Config.get("TENT_WIDTH_M") * Config.get("TENT_HEIGHT_M")
FAN_CAPACITY_M3_PER_MINUTE = Config.get("FAN_CAPACITY_M3_PER_HOUR")/60
AIR_EXCHANGE_PERIOD_MINUTES = 60/Config.get("AIR_EXCHANGES_PER_HOUR")
AIR_EXCHANGE_DURATION_MINUTES = TENT_VOLUME_M3/FAN_CAPACITY_M3_PER_MINUTE


def gpioSetup():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    for gpio in [Config.get("HUMIDIFIER_GPIO"), Config.get("VENTILATOR_GPIO"), Config.get("SENSOR_DHT22_GPIO")]:
        GPIO.setup(gpio, GPIO.OUT)
    return True


def relayON(gpioNumber):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpioNumber, GPIO.OUT)
    GPIO.output(gpioNumber, GPIO.LOW)
    return True


def relayOFF(gpioNumber):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpioNumber, GPIO.OUT)
    GPIO.output(gpioNumber, GPIO.HIGH)
    return False


def ventilatorController(relayStatus):
    while True:
        print("TURNING VENTILATOR ON")
        relayON(Config.get("VENTILATOR_GPIO"))
        time.sleep(AIR_EXCHANGE_DURATION_MINUTES * 60)
        print("TURNING VENTILATOR OFF")
        relayOFF(Config.get("VENTILATOR_GPIO"))
        time.sleep((AIR_EXCHANGE_PERIOD_MINUTES - AIR_EXCHANGE_DURATION_MINUTES) * 60)
        print("NEXT")
        

def sensorController(relayStatus):
    while True:
        sensor = Adafruit_DHT.DHT22
        timeStamp = datetime.datetime.now()
        resultHumidity, resultTemperature = Adafruit_DHT.read_retry(
            sensor, Config.get("SENSOR_DHT22_GPIO"))
        if (resultHumidity and resultTemperature == None) or resultHumidity > 100:
            print("Faulty Measurement")
            time.sleep(10)
        else:
            resultHumidity = round(resultHumidity, 2)
            resultTemperature = round(resultTemperature, 2)
            print("rh:{}, °C:{}, time:{}".format(
                resultHumidity, resultTemperature, timeStamp))
            if resultHumidity < Config.get("IDEAL_HUMIDITY_POINT"):
                relayStatus = relayON(Config.get("HUMIDIFIER_GPIO"))
            elif resultHumidity > Config.get("IDEAL_HUMIDITY_POINT"):
                relayStatus = relayOFF(Config.get("HUMIDIFIER_GPIO"))
            else:
                pass
        time.sleep(5)


def main():
    try:
        if gpioSetup():
            relayStatus = False
            t1 = threading.Thread(target=sensorController, args=[relayStatus,])
            t2 = threading.Thread(target=ventilatorController, args=[relayStatus,])
        t1.start()
        t2.start()
    except RuntimeError:
        print("The GPIOs specified have not been set up")
    except TypeError:
        print("A sensor is not reading properly")


try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    print("Cancelled by the user, cleaning")
finally:
    GPIO.cleanup()



