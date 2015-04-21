import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

redLed = 4 # pin 7
greenLed = 3 # pin 5

startButton = 2 # pin 3 
stopButton = 10 # pin 19

startSensor = 22 # pin 15
stopSensor = 23 # pin 16

# LEDs
GPIO.setup(greenLed, GPIO.OUT)
GPIO.setup(redLed, GPIO.OUT, 1)

#Buttons
GPIO.setup(startButton, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(stopButton, GPIO.IN, GPIO.PUD_UP)

# Sensors
GPIO.setup(startSensor, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(stopSensor, GPIO.IN, GPIO.PUD_UP)


GPIO.output(redLed, 1)


while True:
    print(str(GPIO.input(stopSensor)))




