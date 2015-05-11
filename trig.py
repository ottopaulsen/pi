
import RPi.GPIO as GPIO
import time
import sys
import select
import io
import urllib.request

#URL = 'http://10.0.0.14:8080/'
URL = 'http://192.168.10.102:8080/'

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

redLed = 4 # pin 7
greenLed = 3 # pin 5

#startButton = 2 # pin 3 
#startButton = 11 # pin 23
#stopButton = 10 # pin 19

startButton = 10
stopButton = 11

# LEDs
GPIO.setup(greenLed, GPIO.OUT)
GPIO.setup(redLed, GPIO.OUT)

#Buttons
GPIO.setup(startButton, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(stopButton,  GPIO.IN, GPIO.PUD_UP)


GPIO.output(greenLed, 1)
time.sleep(1)
GPIO.output(greenLed, 0)
GPIO.output(redLed, 1)
time.sleep(1)
GPIO.output(redLed, 0)

timing = False
startTime = 0


def startSignalReceived(channel) :
    print("Start pressed")
    headers = {}
    startTime = time.time()
    req = urllib.request.Request(URL + 'start?time=', None, headers)
    print(urllib.request.urlopen(req).read())
    timing = True

def stopSignalReceived(channel) :
    # Take time and send stop
    print("Stop pressed")
    headers = {}
    req = urllib.request.Request(URL + 'stop?time=' + str(time.time() - startTime), None, headers)
    print(urllib.request.urlopen(req).read())
    timing = False

GPIO.add_event_detect(startButton, GPIO.FALLING, callback=startSignalReceived, bouncetime=300)
GPIO.add_event_detect(stopButton, GPIO.FALLING, callback=stopSignalReceived, bouncetime=300)
#GPIO.add_event_detect(startButton, GPIO.RISING, callback=startSignalReceived, bouncetime=300)
#GPIO.add_event_detect(stopButton, GPIO.RISING, callback=stopSignalReceived, bouncetime=300)



print("Starting loop.")

while True:

    if timing:
        # Send time info to camera
        headers = {}
        req = urllib.request.Request(URL + 'annotate?time=' + str(time.time() - startTime), None, headers)


#    GPIO.output(greenLed, timing)
#    GPIO.output(redLed, (GPIO.input(stopButton) or GPIO(startButton)))




