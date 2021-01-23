import os
import csv
import time
import datetime
import Adafruit_DHT
import RPi.GPIO as GPIO
from ConfigurationHandler import loadConfigData

Config = loadConfigData()

TENT_VOLUME_M3 = Config.get("TENT_LENGHT_M") * Config.get("TENT_WIDTH_M") * Config.get("TENT_HEIGHT_M")
FAN_CAPACITY_M3_PER_MINUTE = Config.get("FAN_CAPACITY_M3_PER_HOUR")/60
AIR_EXCHANGE_PERIOD_MINUTES = 60/Config.get("AIR_EXCHANGES_PER_HOUR")
AIR_EXCHANGE_DURATION_MINUTES = TENT_VOLUME_M3/FAN_CAPACITY_M3_PER_MINUTE


def gpioSetup():
    GPIO.setmode(GPIO.BCM)
    for gpio in [Config.get("HUMIDIFIER_GPIO"), Config.get("VENTILATOR_GPIO"), Config.get("SENSOR_DHT22_GPIO")]:
        GPIO.setup(gpio, GPIO.OUT)
    return True


def relayON(gpioNumber):
    GPIO.output(gpioNumber, GPIO.LOW)
    return True


def relayOFF(gpioNumber):
    GPIO.output(gpioNumber, GPIO.HIGH)
    return False


def ventilatorController(relayStatus):
    i = 0
    while True:
        print("TURNING ON")
        relayON(Config.get("VENTILATOR_GPIO"))
        time.sleep(5)#(AIR_EXCHANGE_DURATION_MINUTES * 60)
        print("TURNING OFF")
        relayOFF(Config.get("VENTILATOR_GPIO"))
        time.sleep(10)#((AIR_EXCHANGE_PERIOD_MINUTES -
                  #  AIR_EXCHANGE_DURATION_MINUTES) * 60)
        i += 1
        print("NEXT", i)

        # if 6 <= currentTime.hour <= 8 == False and relayStatus == False:
        #     relayStatus = relayON(VENTILATOR_GPIO)
        #     time.sleep(AIR_EXCHANGE_DURATION_MINUTES * 60)
        #     relayStatus = relayOFF(VENTILATOR_GPIO)
        # time.sleep((AIR_EXCHANGE_PERIOD_MINUTES -
        #             AIR_EXCHANGE_DURATION_MINUTES) * 60)
        # i += 1


def sensorController(relayStatus):
    with open('historicalData.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        while True:
            sensor = Adafruit_DHT.DHT22
            timeStamp = datetime.datetime.now()
            resultHumidity, resultTemperature = Adafruit_DHT.read_retry(
                sensor, Config.get("SENSOR_DHT22_GPIO"))
            resultHumidity = round(resultHumidity, 2)
            resultTemperature = round(resultTemperature, 2)
            if resultHumidity == None or resultTemperature == None:
                # If sensor is not meausuring properly, then program sleeps for 2 sec
                time.sleep(2)
            else:
                print("rh:{}, °C:{}, time:{}".format(
                    resultHumidity, resultTemperature, timeStamp))
                if resultHumidity < 80:
                    if relayStatus == True:
                        print("Check integrity of the environment")
                        relayStatus = relayOFF(Config.get("HUMIDIFIER_GPIO"))
                        relayStatus = relayON(Config.get("HUMIDIFIER_GPIO"))
                    else:
                        relayStatus = relayON(Config.get("HUMIDIFIER_GPIO"))
                elif resultHumidity > 80:
                    relayStatus = relayOFF(Config.get("HUMIDIFIER_GPIO"))
                else:
                    pass
            writer.writerow(
                [resultHumidity, resultTemperature, timeStamp, relayStatus])


def main():
    try:
        if gpioSetup():
            relayStatus = False
            sensorController(relayStatus)
            # ventilatorController(relayStatus)
    except KeyboardInterrupt:
        print("Cancelled by the user, cleaning")
    except RuntimeError:
        print("The GPIOs specified have not been set up")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
