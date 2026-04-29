import sys
import flask
import json
import os
import warnings
from flask_socketio import SocketIO, emit
from flask_cors import CORS

args = sys.argv

def load_statuses():
    if os.path.exists('statuses.json'):
        with open('statuses.json', 'r') as f:
            return json.load(f)
    return {"Frank": "Unknown", "Jacob": "Unknown"}


def save_statuses(statuses):
    with open('statuses.json', 'w') as f:
        json.dump(statuses, f)
    return statuses


app = flask.Flask(__name__, static_folder='.', static_url_path='')
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')


@app.route('/')
def root():
    return flask.redirect('/sign')


@app.route('/sign')
def sign():
    return flask.send_from_directory(app.root_path, 'index.html')


@app.route('/status')
def status():
    return flask.jsonify(load_statuses())


@app.route('/update', methods=['POST'])
def update():
    payload = flask.request.get_json(silent=True)
    if not payload:
        return flask.jsonify({"error": "JSON body required"}), 400

    statuses = load_statuses()
    if 'person' in payload and 'status' in payload:
        person = payload['person']
        status_value = payload['status']
        if person not in statuses:
            return flask.jsonify({"error": "Invalid person"}), 400
        statuses[person] = status_value
    else:
        statuses = payload

    save_statuses(statuses)
    socketio.emit('status_update', statuses)
    return flask.jsonify(statuses)


@socketio.on('connect')
def handle_connect():
    emit('status_update', load_statuses())


def watch_status_file():
    last_mtime = None
    last_data = load_statuses()

    if os.path.exists('statuses.json'):
        last_mtime = os.path.getmtime('statuses.json')

    while True:
        socketio.sleep(1)
        if not os.path.exists('statuses.json'):
            continue

        current_mtime = os.path.getmtime('statuses.json')
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            current_data = load_statuses()
            if current_data != last_data:
                last_data = current_data
                socketio.emit('status_update', current_data)
                print('Detected external file change and emitted update.')


if len(args) > 1:
    if args[1] == 'update':
        person, new_status = args[2], args[3]
        current_statuses = load_statuses()
        if person in current_statuses:
            current_statuses[person] = new_status
            save_statuses(current_statuses)
            print(f"Updated {person} to {new_status}")
        else:
            print(f"Invalid person: {person}")
        sys.exit(0)


if __name__ == '__main__':
    socketio.start_background_task(watch_status_file)
    socketio.run(app, host='0.0.0.0', port=5000)
