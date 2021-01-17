import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import datetime
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
ELEMENTS_LIST_GPIO = [HUMIDIFIER_GPIO, VENTILATOR_GPIO, SENSOR_DHT22_GPIO]


relayStatus = False


def gpioSetup():
    GPIO.setmode(GPIO.BCM)
    for gpio in ELEMENTS_LIST_GPIO:
        GPIO.setup(gpio, GPIO.OUT)
    return True


# valores invertidos para activar solamente cambiar high por low y low por high en ON Y OFF
def relayON(gpioNumber):
    GPIO.output(gpioNumber, GPIO.HIGH)
    return True


def relayOFF(gpioNumber):
    GPIO.output(gpioNumber, GPIO.LOW)
    return False


def ventilatorController():
    i = 0
    while True:
        currentTime = datetime.datetime.now()
        print(currentTime, currentTime.hour)
        print(i)
        if not 6 <= currentTime.hour <= 9:
            relayON(VENTILATOR_GPIO)
            time.sleep(AIR_EXCHANGE_DURATION_MINUTES * 60)
            relayOFF(VENTILATOR_GPIO)
        time.sleep((AIR_EXCHANGE_PERIOD_MINUTES -
                    AIR_EXCHANGE_DURATION_MINUTES) * 60)
        i += 1


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
                time.sleep(2)
            else:
                print("rh:{}, °C:{}, time:{}".format(
                    resultHumidity, resultTemperature, timeStamp))
                if resultHumidity < 80:
                    if resultHumidity < 50 and relayStatus == True:
                        time.sleep(0)
                    else:
                        relayStatus = relayOFF(HUMIDIFIER_GPIO)
                        time.sleep(0)
                elif resultHumidity > 80:
                    time.sleep(0)
                    relayStatus = relayON(HUMIDIFIER_GPIO)
                else:
                    pass
            writer.writerow(
                [resultHumidity, resultTemperature, timeStamp, relayStatus])


def main():
    try:
        if gpioSetup():
            relayStatus = False
            # sensorController(relayStatus)
            ventilatorController()
    except KeyboardInterrupt:
        print("Cancelled by the user, cleaning")
    except RuntimeError:
        print("The GPIOs specified have not been set up")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
