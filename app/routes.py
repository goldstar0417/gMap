# Set up the Flask routes and SocketIO events.

from flask import Blueprint, jsonify, send_from_directory, render_template_string
from app import socketio
from ftplib import FTP, error_perm
from app.parser import parse_polygon_file
from dotenv import load_dotenv
import secrets
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
ftp_host = os.getenv("FTP_HOST")
ftp_user = os.getenv("FTP_USER")
ftp_pass = os.getenv("FTP_PASS")
folder_path = os.getenv("FOLDER_PATH")
local_path = os.getenv("LOCAL_PATH")
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

main = Blueprint('main', __name__, static_folder='../static')

latest_polygon = {}

@main.route('/')
def index():
    """
    Serve the main HTML file for the root route.
    """
    nonce = secrets.token_hex(16)  # Generate a random 16-byte nonce
    with open(f"{main.static_folder}/index.html") as f:
        html = f.read()
    return render_template_string(html, nonce=nonce, google_maps_api_key=google_maps_api_key)

@main.route('/style.css')
def css():
    """
    Serve the main HTML file for the root route.
    """
    return send_from_directory(main.static_folder, 'style.css')

@main.route('/get_polygon', methods=['GET'])
def get_polygon():
    """
    API route to fetch the latest polygon data.
    """
    return jsonify(latest_polygon)

def fetch_latest_file(ftp_host, ftp_user, ftp_pass, folder_path, local_path):
    """
    Fetches the latest file from the FTP server and saves it locally.
    """
    try:
        print(f"Connecting to FTP host: {ftp_host}")
        ftp = FTP(ftp_host)
        ftp.login(user=ftp_user, passwd=ftp_pass)
        ftp.cwd(folder_path)
        files = ftp.nlst()
        latest_file = max(files, key=lambda f: ftp.voidcmd(f"MDTM " + f))
        with open(local_path, 'wb') as f:
            ftp.retrbinary(f"RETR " + latest_file, f.write)
        ftp.quit()
        return latest_file
    except error_perm as e:
        print(f"failed connect: {e}")
        return

@socketio.on('polygon_update')
def update_polygon_data():
    """
    Updates the latest polygon data and notifies clients via WebSocket.
    """
    try:
        global latest_polygon
        processed_files = set()
        while True:
            latest_file = fetch_latest_file(ftp_host, ftp_user, ftp_pass, folder_path, local_path)
            try:
                if latest_file not in processed_files:
                    print(f"Processing new file: {latest_file}")
                    processed_files.add(latest_file)
                polygon_data = parse_polygon_file(local_path)
            except Exception as e:
                print(f"failed parse file: {e}")
                continue
            try:
                latest_polygon = polygon_data
                socketio.emit('polygon_update_reply', latest_polygon)
                print(f"socket: {latest_polygon}")
                socketio.sleep(3)
            except Exception as e:
                print(f"failed socketio: {e}")
                continue
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return
