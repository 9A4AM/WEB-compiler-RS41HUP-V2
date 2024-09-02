#-------------------------------------------------------------------------------
# Name:        WEB compiler RS41HUP-v2
# Purpose:
#
# Author:      9A4AM
#
# Created:     02.09.2024
# Copyright:   (c) 9A4AM 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for
import subprocess
import os
import threading
import datetime

app = Flask(__name__)

# Putanje do config.h i drugih datoteka
CONFIG_FILE_PATH = r'C:\Users\9A4AM\Desktop\RS41HUP_V2-9A4AM\config.h'
HEX_FILE_PATH = r'C:\Users\9A4AM\Desktop\RS41HUP_V2-9A3BFT\RS41HUP\Debug\bin\RS41HUP.hex'
BATCH_FILE_PATH = r'C:\Users\9A4AM\Desktop\Online compiler\compile.exe'

# Globalne varijable za praćenje aktivnog korisnika i vremena zadnje aktivnosti
active_user = None
last_active_time = None
lock = threading.Lock()

# Timeout postavka (npr. 5 minuta neaktivnosti)
SESSION_TIMEOUT = datetime.timedelta(minutes=5)

def is_session_active():
    global last_active_time
    if last_active_time:
        return datetime.datetime.now() - last_active_time < SESSION_TIMEOUT
    return False

def release_session():
    global active_user, last_active_time
    with lock:
        active_user = None
        last_active_time = None

@app.route('/')
def index():
    global active_user, last_active_time
    with lock:
        # Provjeri je li sesija aktivna
        if active_user is None or not is_session_active():
            # Rezerviraj trenutnog korisnika
            active_user = request.remote_addr
            last_active_time = datetime.datetime.now()
            return render_template('index.html')
        elif active_user == request.remote_addr:
            # Ako je isti korisnik, dopusti mu pristup i osvježi vrijeme aktivnosti
            last_active_time = datetime.datetime.now()
            return render_template('index.html')
        else:
            # Odbij pristup drugim korisnicima
            return "Another user is currently using the application. Please try again later.", 403

@app.route('/load-config', methods=['GET'])
def load_config():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        return "Access denied.", 403

    last_active_time = datetime.datetime.now()

    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config_content = file.read()
        return jsonify({"content": config_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save-config', methods=['POST'])
def save_config():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        return "Access denied.", 403

    last_active_time = datetime.datetime.now()

    try:
        new_content = request.json.get('content')
        with open(CONFIG_FILE_PATH, 'w') as file:
            file.write(new_content)
        return jsonify({"message": "Config saved successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/compile', methods=['POST'])
def compile_project():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        return "Access denied.", 403

    last_active_time = datetime.datetime.now()

    try:
        result = subprocess.run([BATCH_FILE_PATH], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return jsonify({"message": "Compilation successful.", "status": "success"})
        else:
            return jsonify({"message": "Compilation failed.", "status": "error", "error": result.stderr})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['GET'])
def download_file():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        return "Access denied.", 403

    last_active_time = datetime.datetime.now()

    try:
        return send_file(CONFIG_FILE_PATH, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download-hex', methods=['GET'])
def download_hex():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        return "Access denied.", 403

    last_active_time = datetime.datetime.now()

    try:
        if os.path.exists(HEX_FILE_PATH):
            return send_file(HEX_FILE_PATH, as_attachment=True)
        else:
            return jsonify({"error": "Hex file not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/release', methods=['POST'])
def release_user():
    global active_user
    if active_user == request.remote_addr:
        release_session()
        return "User session released.", 200
    else:
        return "Access denied.", 403

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1180)

