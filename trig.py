
import RPi.GPIO as GPIO
import time, datetime
import sys
import select
import io
import urllib.request
from threading import Timer

URL = 'http://10.0.0.14:8080/'
#URL = 'http://192.168.10.102:8080/'

TIMEFORMAT = '%H:%M:%S.%f'

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

redLed = 4 # pin 7
greenLed = 3 # pin 5

startButton = 2 # pin 3 
#startButton = 11 # pin 23
stopButton = 10 # pin 19


# LEDs
GPIO.setup(greenLed, GPIO.OUT)
GPIO.setup(redLed, GPIO.OUT)

#Buttons
GPIO.setup(startButton, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(stopButton,  GPIO.IN, GPIO.PUD_UP)


GPIO.output(greenLed, 1)
time.sleep(0.2)
GPIO.output(greenLed, 0)
GPIO.output(redLed, 1)
time.sleep(0.2)
GPIO.output(redLed, 0)

timing = False
startTime = 0

def now() :
    return datetime.datetime.now().strftime(TIMEFORMAT)


def startSignalReceived(channel) :
    global startTime, timing
    startTime = time.time()
    print("Start pressed", end = '')
    sys.stdout.flush()
    headers = {}
    req = urllib.request.Request(URL + 'start?time=' + str(startTime), None, headers)
    res = urllib.request.urlopen(req).read()
    timing = True
    print(", processing time " + str(round(time.time() - startTime, 2)) + " seconds. Result: ", res )
    #annotate()

def stopSignalReceived(channel) :
    # Take time and send stop
    global timing
    stopTime = time.time()
    print("Stop pressed", end = '')
    sys.stdout.flush()
    headers = {}
    req = urllib.request.Request(URL + 'stop?time=' + str(stopTime), None, headers)
    res = urllib.request.urlopen(req).read()
    timing = False
    print(",  processing time " + str(round(time.time() - stopTime, 2)) + " seconds. Result: ", res )

GPIO.add_event_detect(startButton, GPIO.FALLING, callback=startSignalReceived, bouncetime=300)
GPIO.add_event_detect(stopButton, GPIO.FALLING, callback=stopSignalReceived, bouncetime=300)
#GPIO.add_event_detect(startButton, GPIO.RISING, callback=startSignalReceived, bouncetime=300)
#GPIO.add_event_detect(stopButton, GPIO.RISING, callback=stopSignalReceived, bouncetime=300)


def annotate() :
    global timing, startTime
    if timing :
        # Send time info to camera
        now = time.time()
        printTime = str(round(now - startTime, 2))
        headers = {}
        #print("Kaller annotate?time=", printTime)
        req = urllib.request.Request(URL + 'annotate?time=' + printTime, None, headers)
        res = urllib.request.urlopen(req).read()
        t = Timer(0.1, annotate)
        t.start()        

print("Starting loop.")


while True:
    pass



#    GPIO.output(greenLed, timing)
#    GPIO.output(redLed, (GPIO.input(stopButton) or GPIO(startButton)))




