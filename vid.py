from bottle import Bottle, run, static_file, template, request, sys
from oputils import stringToInt
import time, picamera, io
import os.path

STATUS_STARTING = 0
STATUS_WAITING = 1
STATUS_STARTED = 2
STATUS_STOPPING = 3
STATUS_STOPPED = 4
status = STATUS_STARTING

VIDEOFORMAT = "h264"
FRAMERATE = 25
camera = picamera.PiCamera(framerate = FRAMERATE)
camera.resolution = (640, 480)
#camera.hflip = True
#camera.vflip = True
stream = picamera.PiCameraCircularIO(camera, seconds=120)
videoCounter = 0

app = Bottle()


# Return filename for the next video to be recorded
def getFilename(fileEnding = 'h264'):
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
        camera.start_recording(stream, format = VIDEOFORMAT)
        status = STATUS_WAITING
        print ("Recording to buffer starting at " + getPrintableTime())

def getCurrentFrameIndex(stream) :
    global camera
    res = 0
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
    bytesToSave = 0
    with stream.lock :
        for frame in stream.frames :
            if frame.frame_type == picamera.PiVideoFrameType.sps_header :
                lastSpsHeader = frame.position
                if frame.index <= start :
                    bytesToSave = 0
            bytesToSave += frame.frame_size
            if frame.index >= start and startPosition is None : 
                if lastSpsHeader is not None : 
                    startPosition = lastSpsHeader
            if frame.index >= stop :
                break
        if startPosition is not None :
            print("Saving file " + getFilename() + ", frame " + str(start) + " to " + str(stop) + ", in total " + str(bytesToSave) + " bytes from position " + str(startPosition))
            stream.seek(startPosition)
            with io.open(getFilename(), 'wb') as output :
                output.write(stream.read(bytesToSave))


@app.route('/start')
def start():
    global status, videoStartFrame, stream, startTime, camera
    res = "Busy. Cannot start."
    if status == STATUS_WAITING :
        status = STATUS_STARTED
        offset = stringToInt(request.query.offset, 0)
        startTime = stringToInt(request.query.time, 0)
        videoStartFrame = getCurrentFrameIndex(stream) + offset * FRAMERATE
        res = "Video start frame: " + str(videoStartFrame)
        camera.annotate_text = "Time: " + str(startTime)
    print(res)
    return res

@app.route('/stop')
def stop():
    global camera, stream, output, status, videoStartFrame, startTime
    res = "Not started. Cannot stop."
    if status == STATUS_STARTED :
        status = STATUS_STOPPING
        offset = stringToInt(request.query.offset, 0)
        stopTime = stringToInt(request.query.time, 0)
        videoStopFrame = getCurrentFrameIndex(stream) + offset * FRAMERATE
        videoLength = videoStopFrame - videoStartFrame
        if stopTime > 0 :
            runTime = stopTime - startTime
            camera.annotate_text = "Time: " + str(runTime)
            print("Run time: " + str(runTime))
        if offset > 0 :
            print("Camera running " + str(offset) + " more seconds")               
            camera.wait_recording(offset)
        res = "Video stop frame: " + str(videoStopFrame)
        saveVideo(stream, videoStartFrame, videoStopFrame)
        camera.annotate_text = "Waiting"
        status = STATUS_WAITING
    print(res)
    return res

@app.route('/annotate')
def annotate():
    global camera
    if request.query.time is not None :
        camera.annotate_text = "Time: " + request.query.time
    else :
        camera.annotate_text = request.query.annotate
    return camera.annotate_text

@app.route('/view')
def view():
    filename = request.query.filename
    print("View video file: " + filename)
    res = '''
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <title>View video</title>
            </head>

            <body>
                <video width="640" height="480" autoplay preload="auto" controls>
                    <source src="http://10.0.0.14:8081/''' + filename + '''" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </body>

        </html>

    '''

#                <video width="960" height="540" autoplay preload="auto" src="http://10.0.0.14:8080/home/pi/fart/''' + filename + '''">


    return(res)

@app.route('/files/<filename>')
def send_file(filename) :
    print("Serving file: " + filename)
    return static_file(filename, root='/home/pi/fart', mimetype='video/mp4')


@app.route('/terminate')
def terminate() :
    print("Terminating!")
    sys.stderr.close()

@app.route('/preview/<function>')
def preview(function):
    if function.lower() == 'on':
        camera.start_preview()
        return "Preview started"
    elif function.lower() == 'off':
        camera.stop_preview()
        return "Preview stopped"

reset(stream)
run(app, host='0.0.0.0', port=8080, debug=True)
