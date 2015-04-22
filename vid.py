from bottle import route, run
import time, picamera, io

camera = picamera.PiCamera()
#camera.brightness = 60
camera.hflip = True
camera.vflip = True
stream = picamera.PiCameraCircularIO(camera, seconds=20)
camera.start_recording(stream, format='h264')
print ("Camera started, recording to buffer")
camera.wait_recording(1)
stopped = False
timing = False
startTime = time.time()
stopTime = startTime
runTime = startTime
videoCounter = 1
print ("Ready (time:" + str(startTime) + ")!")

@route('/start')
def start():
	res = "Already started. Cannot start again until stopped."
	if not timing:
		startTime = time.time()
		timing = True
		stopped = False
		print("Start: " + str(startTime))
		camera.annotate_text = 'Timer started'
		res = "Started at " + str(startTime)
	return res

@route('/stop')
def stop():
	res = "Not started. Cannot stop."
	if timing and not stopped:
		stopTime = time.time()
		runTime = stopTime - startTime
		print("Stop:  " + str(stopTime))
		print("Run time: " + str(runTime))
		camera.annotate_text = 'Timer stopped'
		stopped = True
		print("Camera running 5 more seconds")
		camera.wait_recording(5)
		camera.stop_recording()
		videoCounter += 1
		res = "Stopped at " + str(stopTime)
	return res

run(host='0.0.0.0', port=8080, debug=True)
