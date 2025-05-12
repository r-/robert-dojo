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
app.register_blueprint(dojocontrol_bp)


lock = threading.Lock()
server_ip = ""

players = {}
app.config['PLAYERS'] = players
logs = []
app.config['LOGS'] = logs
score = {
    "0": 0,
    "1": 0
}
app.config['SCORE'] = score


def get_server_ip():
    """Get the server's public IP address."""
    return socket.gethostbyname(socket.gethostname())

@app.route('/get_game_data', methods=['GET'])
def get_game_data():
    """Provide updated logs and connected players."""
    return jsonify({
        'players': players,
        'logs': logs,
        'score': score
    })

@app.route('/')
def index():
    global server_ip
    """Render the home page where players can view the game state."""
    server_ip = get_server_ip()
    print(server_ip)
    #simulate_login()
    return render_template('index.html', players=players, logs=logs, server_ip=server_ip)

def simulate_login():
    global server_ip
    for x in range(5):
        login_data = {"command": f"/login 127.0.0.{x+2} {x+2}"}
        print(login_data)
        entire_string = f"http://{server_ip}:5001/command"
        print(entire_string)
        response = requests.post(entire_string, json=login_data)
        #if response.status_code == 200:
        #    return jsonify({"status": "success", "message": f"Logged in successfully as Player {x} to 127.0.0.1."})
        #else:
        #    return jsonify({"status": "error", "message": "Failed to connect to the server."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
