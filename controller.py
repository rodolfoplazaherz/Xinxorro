import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import os

relayStatus = False

def gpioSetup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.OUT)
    GPIO.output(27, GPIO.LOW)
    return print("Setup Complete!")


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
    import csv
    with open('historicalData.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        while True:
            time.sleep(2)
            sensor = Adafruit_DHT.DHT22
            timeStamp = time.time()
            # activar el ventilador cada hora
            timeElapsed = time.time() - initTime
            print(initTime, timeElapsed)

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
                elif resultHumidity > 85 and relayStatus == True:
                    waitXSeconds(0)
                    relayStatus = relayOFF(27)
                    print('High humidity, turning OFF the relay')
                elif 80 <= resultHumidity <= 85:
                    relayStatus = relayOFF(27)
                    print("Perfect Humidity, relayOFF")
                else:
                    pass
except KeyboardInterrupt:
    print('cancelled by the user, cleaning')
finally:
    GPIO.cleanup()
