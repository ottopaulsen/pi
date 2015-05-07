from bottle import Bottle, run, request
import picamera

app = Bottle()
camera = picamera.PiCamera(framerate = 30)
stream = picamera.PiCameraCircularIO(camera, seconds=600)
camera.start_recording(stream, format = 'h264')

@app.route('/view')
def view():
    filename = request.query.filename
    print("View video file: " + filename)
    res = '''
        <html>
            <head>
                <title>View video</title>
            </head>
            <body>
                <video width="640" height="480" controls>
                    <source src="http://10.0.0.14:8080/video?fromframe=30&toframe=330" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </body>
        </html>
    '''
    return(res)

@app.route('/video')
def video() :
    fromFrame = request.query.fromframe
    toFrame = request.query.toframe
    print("Sending from fram " + str(fromFrame) + " to frame " + str(toFrame))
    return "WHAT DO I DO HERE?"

run(app, host='0.0.0.0', port=8080, debug=True)
