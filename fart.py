
import RPi.GPIO as GPIO
import time
import picamera
import sys
import select
import io

from op_keyboard import read_single_keypress


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

camera = picamera.PiCamera()
#camera.brightness = 60
camera.hflip = True
camera.vflip = True

GPIO.output(greenLed, 1)
time.sleep(1)
GPIO.output(greenLed, 0)
GPIO.output(redLed, 1)
time.sleep(1)
GPIO.output(redLed, 0)

timing = False

videoCounter = 0



def write_video1(stream):
    print('Writing video!')
    with stream.lock:
        # Find the first header frame in the video
        for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break
        # Write the rest of the stream to disk
        with io.open('video.h264', 'wb') as output:
            output.write(stream.read())


def write_video2(stream):
    # Write the entire content of the circular buffer to disk. No need to
    # lock the stream here as we're definitely not writing to it
    # simultaneously
    print('Writing video before!')
    with io.open('before.h264', 'wb') as output:
        for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break
        while True:
            buf = stream.read1()
            if not buf:
                break
            output.write(buf)
    # Wipe the circular stream once we're done
    stream.seek(0)
    stream.truncate()


stream = picamera.PiCameraCircularIO(camera, seconds=20)
camera.start_recording(stream, format='h264')
print ("Recording started")
camera.wait_recording(1)

c = ''
stopped = False
timing = False

print("Starting loop. Press t to terminate, i to start, o to stop.")

while c != 't':

    c = read_single_keypress()


    Denne fortsetter bare når det trykkes tast. Må skrive om.

    if GPIO.input(startButton) == False or c == 'i' :
    	if not timing:
    	    startTime = time.time()
    	    timing = True
            stopped = False
            print("Start: " + str(startTime))
            camera.annotate_text = 'Timer started'
            #write_video2(stream)
            #print("Splitting video")
            #camera.split_recording('after.h264')

            videoCounter += 1

    if timing:
        print('Posisjon: ' + str(stream.tell()))
        #camera.annotate_text = str(startTime - time.time())

    if GPIO.input(stopButton) == False or c == 'o':
    	if timing and not stopped:
    	    stopTime = time.time()
    	    #timing = False
    	    runTime = stopTime - startTime
    	    print("Stop:  " + str(stopTime))
    	    print("Run time: " + str(runTime))
            camera.annotate_text = 'Timer stopped'
            #camera.wait_recording(5)
            #camera.stop_recording()
            print("Stopped recording in 5 sek")
            stopped = True

    if timing and stopped:
        if time.time() - stopTime > 5:
            camera.stop_recording()
            write_video1(stream)
            timing = False

    GPIO.output(greenLed, GPIO.input(startButton))
    GPIO.output(redLed, GPIO.input(stopButton))




