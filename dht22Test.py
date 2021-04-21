import Adafruit_DHT
import RPi.GPIO as GPIO
import time

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.OUT)
    i=0
    while True:
        sensor = Adafruit_DHT.DHT22
        resultHumidity, resultTemperature = Adafruit_DHT.read_retry(sensor, 27)
        if resultHumidity and resultTemperature == None:
            pass
        else:
            resultHumidity = round(resultHumidity)
            resultTemperature = round(resultTemperature)
        print(resultHumidity, resultTemperature, i)
        i += 1
        time.sleep(5)
except KeyboardInterrupt:
    print("cancelled")
finally:
    GPIO.cleanup()