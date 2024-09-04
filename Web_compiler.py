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
import logging

app = Flask(__name__)

# Putanje do config.h i drugih datoteka
CONFIG_FILE_PATH = r'path\to\your\RS41HUP-V2\config.h'
CONFIG_ORG_PATH = r'path\to\your\RS41HUP-V2\config_org.h'
HEX_FILE_PATH = r'\path\to\your\RS41HUP-V2\\build\output.hex'
BATCH_FILE_PATH = r'\path\to\your\project\compile_project.bat'

# Postavke za logiranje
LOG_FILE_PATH = r'\path\to\your\project\log.txt'
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_activity(message):
    logging.info(message)

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
        log_activity("Session released")
        # Pokreni reset_config.h nakon završetka sesije
        reset_config()


def reset_config():
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
        os.system(f'copy "{CONFIG_ORG_PATH}" "{CONFIG_FILE_PATH}"')
        log_activity("config.h restore to default")
    except Exception as e:
        print(f"Error resetting config: {e}")

@app.route('/')
def index():
    global active_user, last_active_time
    with lock:
        if active_user is None or not is_session_active():
            active_user = request.remote_addr
            last_active_time = datetime.datetime.now()
            log_activity(f"User connected from IP: {request.remote_addr}")
            return render_template('index.html')
        elif active_user == request.remote_addr:
            last_active_time = datetime.datetime.now()
            return render_template('index.html')
        else:
            log_activity(f"Access attempt by {request.remote_addr} denied. Session is active by another user.")
            return "Sorry!! Another user is currently using the application. Please try again later.", 403

@app.route('/load-config', methods=['GET'])
def load_config():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        log_activity(f"Unauthorized access attempt to load config by IP: {request.remote_addr}")
        return "Access denied.", 403
    reset_config()
    last_active_time = datetime.datetime.now()
    log_activity(f"Config file loaded by IP: {request.remote_addr}")

    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config_content = file.read()
        return jsonify({"content": config_content})
    except Exception as e:
        log_activity(f"Error loading config: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/save-config', methods=['POST'])
def save_config():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        log_activity(f"Unauthorized access attempt to save config by IP: {request.remote_addr}")
        return "Access denied.", 403

    last_active_time = datetime.datetime.now()
    log_activity(f"Config file saved by IP: {request.remote_addr}")

    try:
        new_content = request.json.get('content')
        with open(CONFIG_FILE_PATH, 'w') as file:
            file.write(new_content)
        return jsonify({"message": "Config saved successfully."})
    except Exception as e:
        log_activity(f"Error saving config: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/compile', methods=['POST'])
def compile_project():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        log_activity(f"Unauthorized compile attempt by IP: {request.remote_addr}")
        return "Access denied.", 403

    last_active_time = datetime.datetime.now()
    log_activity(f"Compilation started by IP: {request.remote_addr}")

    try:
        result = subprocess.run([BATCH_FILE_PATH], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            log_activity(f"Compilation successful by IP: {request.remote_addr}")
            return jsonify({"message": "Compilation successful.", "status": "success"})
        else:
            log_activity(f"Compilation failed by IP: {request.remote_addr}. Error: {result.stderr}")
            return jsonify({"message": "Compilation failed.", "status": "error", "error": result.stderr})
    except Exception as e:
        log_activity(f"Error during compilation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['GET'])
def download_file():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        log_activity(f"Unauthorized download attempt by IP: {request.remote_addr}")
        return "Access denied.", 403

    last_active_time = datetime.datetime.now()
    log_activity(f"Config file downloaded by IP: {request.remote_addr}")

    try:
        return send_file(CONFIG_FILE_PATH, as_attachment=True)
    except Exception as e:
        log_activity(f"Error downloading config file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download-hex', methods=['GET'])
def download_hex():
    global active_user, last_active_time
    if active_user != request.remote_addr or not is_session_active():
        release_session()
        log_activity(f"Unauthorized hex download attempt by IP: {request.remote_addr}")
        return "Access denied.", 403

    last_active_time = datetime.datetime.now()
    log_activity(f"Hex file downloaded by IP: {request.remote_addr}")

    try:
        if os.path.exists(HEX_FILE_PATH):
            return send_file(HEX_FILE_PATH, as_attachment=True)
        else:
            log_activity(f"Hex file not found for download by IP: {request.remote_addr}")
            return jsonify({"error": "Hex file not found."}), 404
    except Exception as e:
        log_activity(f"Error downloading hex file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/release', methods=['POST'])
def release_user():
    global active_user
    if active_user == request.remote_addr:
        log_activity(f"Session released by IP: {request.remote_addr}")
        release_session()
        return "User session released.", 200
    else:
        log_activity(f"Unauthorized session release attempt by IP: {request.remote_addr}")
        return "Access denied.", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1180)
