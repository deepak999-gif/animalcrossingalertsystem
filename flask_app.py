from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import signal
import os

app = Flask(__name__)
alerts = []
detector_process = None

@app.route('/')
def index():
    return render_template('index.html', alerts=alerts)

@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    alerts.insert(0, data)
    return {'status': 'ok'}

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global detector_process
    if detector_process is None or detector_process.poll() is not None:
        detector_process = subprocess.Popen(['python', 'animal_detector.py'])
        return jsonify({'status': 'started'})
    else:
        return jsonify({'status': 'already running'})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global detector_process
    if detector_process and detector_process.poll() is None:
        detector_process.terminate()
        detector_process = None
        return jsonify({'status': 'stopped'})
    else:
        return jsonify({'status': 'not running'})

if __name__ == '__main__':
    app.run(debug=True)
