
import RPi.GPIO as GPIO
import time
import sys
import select
import io
import urllib2

URL = 'http://10.0.0.14:8080/'

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

redLed = 4 # pin 7
greenLed = 3 # pin 5

startButton = 2 # pin 3 
stopButton = 10 # pin 19

# LEDs
GPIO.setup(greenLed, GPIO.OUT)
GPIO.setup(redLed, GPIO.OUT)

#Buttons
GPIO.setup(startButton, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(stopButton, GPIO.IN, GPIO.PUD_UP)


GPIO.output(greenLed, 1)
time.sleep(1)
GPIO.output(greenLed, 0)
GPIO.output(redLed, 1)
time.sleep(1)
GPIO.output(redLed, 0)

timing = False
startTime = 0

print("Starting loop.")

while True:

    if GPIO.input(startButton) == False :
        # Take time and send start call
        headers = {}
        startTime = time.time()
        req = urllib2.Request(URL + 'start?time=', None, headers)
        print(urllib2.urlopen(req).read())
        timing = True

    if timing:
        # Send time info to camera
        headers = {}
        req = urllib2.Request(URL + 'annotate?time=' + str(time.time() - startTime), None, headers)

    if GPIO.input(stopButton) == False :
        # Take time and send stop
        headers = {}
        req = urllib2.Request(URL + 'stop?time=' + str(time.time() - startTime), None, headers)
        print(urllib2.urlopen(req).read())
        timing = False

    GPIO.output(greenLed, timing)
    GPIO.output(redLed, GPIO.input(stopButton) or GPIO(startButton))




