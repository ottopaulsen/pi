from bottle import route, run, static_file
import time, picamera, io

camera = picamera.PiCamera(framerate = 25)
#camera.brightness = 60
camera.hflip = True
camera.vflip = True
stream = picamera.PiCameraCircularIO(camera, seconds=5)
camera.annotate_text = "Buffering video"
camera.start_recording(stream, format='h264')
print ("Camera started, recording to buffer")
camera.wait_recording(1)
stopped = False
timing = False
startTime = time.time()
stopTime = startTime
runTime = startTime
videoCounter = 0
filename = "video-0.h264"


print ("Ready (time:" + str(startTime) + ")!")

def write_buf_to_file(stream, filename):
	global output
	with stream.lock:
    	# Find the first header frame in the video
	    for frame in stream.frames:
	        if frame.frame_type == picamera.PiVideoFrameType.sps_header:
	            stream.seek(frame.position)
	            break
	    # Write the rest of the stream to disk
	    output = io.open(filename, 'wb')
        output.write(stream.read())
	return output
	

@route('/start')
def start():
	global camera, stream, stopped, timing, startTime, videoCounter, filename, output
	res = "Already started. Cannot start again until stopped."
	if not timing:
		startTime = time.time()
		timing = True
		stopped = False
		videoCounter += 1
		filename = "video-" + str(videoCounter) + ".h264"
		print("Start: " + str(startTime))
		camera.annotate_text = 'Timer started'
		output = write_buf_to_file(stream, filename)
		camera.split_recording(output)
		res = "Started at " + str(startTime)
	return res

@route('/stop')
def stop():
	global camera, stream, stopped, timing, stopTime, runTime, videoCounter, output
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
		output.close()
		res = "Stopped at " + str(stopTime) + ", run time " + str(runTime)
	return res

@route('/view')
def view():
	global filename
	return(static_file(filename, root = "/home/pi/fart"))

run(host='0.0.0.0', port=8080, debug=True)
