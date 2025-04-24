import socket
from flask import Flask, jsonify, request, render_template, send_file, Blueprint
from flask_cors import CORS
from PIL import Image
from pyzbar.pyzbar import decode
import threading
import requests

app = Flask(__name__)
CORS(app)

from tools.QR_Codes import qrcode_bp
#from tools.test import test_bp
from tools.commands import command_bp
from tools.dojocontrol import dojocontrol_bp

app.register_blueprint(qrcode_bp)
#app.register_blueprint(test_bp)
app.register_blueprint(command_bp)
#app.register_blueprint(dojocontrol_bp)

players = {}
lock = threading.Lock()

logs = []

def get_server_ip():
    """Get the server's public IP address."""
    return socket.gethostbyname(socket.gethostname())

@app.route('/get_game_data', methods=['GET'])
def get_game_data():
    """Provide updated logs and connected players."""
    return jsonify({
        'players': players,
        'logs': logs
    })

@app.route('/')
def index():
    """Render the home page where players can view the game state."""
    server_ip = get_server_ip()
    return render_template('index.html', players=players, logs=logs, server_ip=server_ip)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
