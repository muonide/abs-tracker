from flask import *
from flask_socketio import SocketIO
import time
import datetime
import json
import serial
import pynmea2
import rockBlock

from rockBlock import rockBlockProtocol


serialStream = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)

app = Flask(__name__)
socketio = SocketIO(app)


longitude = 0.0
latitude = 0.0
altitude = 0.0
start = time.time()

@app.route("/")
def index():
        return render_template('index.html')

@app.route('/balloon')
def balloon():
        def read_balloon_update():
            while True:
                get_update()
                iridiumEmit(data)
                balloon_update ={ 'longitude' : longitude,
                                'latitude' : latitude,
                                'altitude' : altitude,
                                'elapse' : get_elapse()  }
                time.sleep(30)
                yield 'data:{0}\n\n'.format(json.dumps(balloon_update))
        return Response(read_balloon_update(), mimetype='text/event-stream')

def get_update():
    sentence = serialStream.readline()
    if sentence.find('GGA') > 0:
        data = pynmea2.parse(sentence)
        gpstime = data.timestamp
        longitude = data.longitude
        latitude = data.latitude
        altitude = data.altitude
        timelog = data.time
        ##add file storage of data here
        with open('flightData.json','a') as outfile:
            json.dump(data, outfile, sort_keys = True, indent = 4, ensure_ascii = False)

    return data

def get_elapse():
    return time.time() - start

def iridiumEmit(self, value):
    rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
    rb.sendMessage(str(gpstime)+","+str(longitude)+","+str(latitude)+","+str(altitude))
    rb.close()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)

