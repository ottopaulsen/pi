from bottle import route, run, static_file, template, request
from oputils import stringToInt
import time, picamera, io
import os.path

STATUS_STARTING = 0
STATUS_WAITING = 1
STATUS_STARTED = 2
STATUS_STOPPING = 3
STATUS_STOPPED = 4

camera = picamera.PiCamera(framerate = 25)
camera.hflip = True
camera.vflip = True

stream = picamera.PiCameraCircularIO(camera, seconds=120)


status = STATUS_STARTING
videoCounter = 0


# Return filename for the next video to be recorded
def getFilename(fileEnding = "h264"):
	global videoCounter
	fileName =  "video-" + str(videoCounter) + "." + fileEnding
	while os.path.exists(fileName) :
		videoCounter += 1
		fileName =  "video-" + str(videoCounter) + "." + fileEnding
	return fileName

# Return time in text format, for printing timings
def getPrintableTime(timeToGet = None) :
	if timeToGet == None : timeToGet = time.time()
	t = time.localtime(timeToGet)
	return str(t.tm_hour) + ":" + \
	       str(t.tm_min)  + ":" + \
	       str(t.tm_sec)  + "." + \
	       str(int((timeToGet - int(timeToGet)) * 100))


def reset(stream) :
	global videoCounter, camera, status
	if status == STATUS_STARTING :
		camera.start_recording(stream, format='h264')
		status = STATUS_WAITING
		print ("Recording to buffer starting at " + getPrintableTime())


def write_buf_to_file(stream, filename):
	global output
	with stream.lock:
    	# Find the first header frame in the video
	    for frame in stream.frames:
	        if frame.frame_type == picamera.PiVideoFrameType.sps_header :
	            stream.seek(frame.position)
	            break
	    # Write the rest of the stream to disk
	    output = io.open(filename, 'wb')
        output.write(stream.read())
	return output

def getCurrentFrameIndex(stream) :
	global camera
	res = 0L
	with stream.lock :
		for frame in stream.frames :
			pass
		res = frame.index 
	#print("Frame: " + str(res))
	return res

def saveVideo(stream, start, stop) :
	global videoCounter
	videoCounter += 1
	print("Saving from " + str(start) + " to " + str(stop))
	lastSpsHeader = None
	startPosition = None
	bytesToSave = 0L
	with stream.lock :
	    for frame in stream.frames :
			#print("Frame " + str(frame.index) + ", size " + str(frame.frame_size))
			if frame.frame_type == picamera.PiVideoFrameType.sps_header :
				lastSpsHeader = frame.position
				#print("SPS frame " + str(frame.index))
				if frame.index <= start :
					bytesToSave = 0L
					#print("Nullstiller")
			bytesToSave += frame.frame_size
			#if startPosition is not None : print ("Bytes to save: " + str(bytesToSave))
			if frame.index >= start and startPosition is None : 
				if lastSpsHeader is not None : 
					startPosition = lastSpsHeader
			if frame.index >= stop :
				break
	    if startPosition is not None :
	    	print("Saving frame " + str(start) + " to " + str(stop) + ", in total " + str(bytesToSave) + " bytes from position " + str(startPosition))
	    	stream.seek(startPosition)
	    	with io.open(getFilename(), 'wb') as output :
    			output.write(stream.read(bytesToSave))



reset(stream)

@route('/start')
def start():
	global status, startTime, videoStartFrame, stream
	res = "Busy. Cannot start."
	if status == STATUS_WAITING :
		status = STATUS_STARTED
		startTime = time.time()
		offset = stringToInt(request.query.offset, 0)
		videoStartFrame = getCurrentFrameIndex(stream)
		res = "Start time: " + getPrintableTime(startTime) + "\nVideo start frame: " + str(videoStartFrame)
	print(res)
	return res

@route('/stop')
def stop():
	global camera, stream, stopTime, runTime, output, status, videoStartFrame, startTime
	res = "Not started. Cannot stop."
	if status == STATUS_STARTED :
		status = STATUS_STOPPING
		stopTime = time.time()
		offset = stringToInt(request.query.offset, 0)
		videoStopFrame = getCurrentFrameIndex(stream)
		runTime = stopTime - startTime
		videoLength = videoStopFrame - videoStartFrame
		print("Stop:  " + getPrintableTime(stopTime))
		if offset > 0 :
			print("Camera running " + str(offset) + " more seconds")
			camera.wait_recording(offset)
		res = "Stop time: " + getPrintableTime(stopTime) + "\nVideo stop frame:" + str(videoStopFrame)
		saveVideo(stream, videoStartFrame, videoStopFrame)
		status = STATUS_WAITING
	print(res)
	return res

@route('/view')
def view():
	global filename
	return(static_file(filename, root = "/home/pi/fart"))

@route('/terminate')
def terminate() :
	print("Terminating!")
	bottle.Bottle.close()

@route('/preview/<function>')
def preview(function):
	if function.lower() == 'on':
		camera.start_preview()
		return "Preview started"
	elif function.lower() == 'off':
		camera.stop_preview()
		return "Preview stopped"

@route('/init')
def init() :
	global stream
	reset(stream)
	return "Stream reset"

run(host='0.0.0.0', port=8080, debug=True)
