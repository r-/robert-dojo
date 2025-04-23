import socket
from flask import Flask, jsonify, request, render_template, send_file, Blueprint
from flask_cors import CORS
from PIL import Image
from pyzbar.pyzbar import decode
import threading
import numpy as np
import qrcode
import requests
import hashlib
import cv2
import cv2.aruco as aruco
from tools.QR_Codes import qrcode_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(qrcode_bp)

players = {}
lock = threading.Lock()

logs = []

# Server-side update_health function
def update_health(player_id):
    """Update the health of a player by notifying the client via set_health."""
    if player_id not in players:
        app.logger.error(f"Player '{player_id}' not found.")
        return jsonify({"status": "error", "message": f"Player '{player_id}' not found."}), 404

    player = players[player_id]
    health = player["health"]
    player_ip = player["ip"]

    client_url = f"http://{player_ip}:5000/network/set_health"
    print(client_url)

    data = {
        'status': health  # Send the health value directly under 'status'
    }

    try:
        response = requests.post(client_url, json=data)
        if response.status_code == 200:
            print(f"Successfully updated health for player {player_id} to {health}.")
            app.logger.info(f"Successfully updated health for player {player_id} to {health}.")
            return jsonify({"status": "success", "message": f"Health of player {player_id} updated successfully."})
        else:
            print(f"Failed to update health for player {player_id}: {response.text}")
            app.logger.error(f"Failed to update health for player {player_id}: {response.text}")
            return jsonify({"status": "error", "message": "Failed to update health on client."}), 500
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error updating health for player {player_id}: {e}")
        return jsonify({"status": "error", "message": f"Error communicating with client: {str(e)}"}), 500

ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

@app.route('/')
def index():
    """Render the home page where players can view the game state."""
    server_ip = get_server_ip()
    return render_template('index.html', players=players, logs=logs, server_ip=server_ip)

def get_server_ip():
    """Get the server's public IP address."""
    return socket.gethostbyname(socket.gethostname())

@app.route('/command', methods=['OPTIONS', 'POST'])
def command():
    global players
    print("Command recieved")
    if request.method == 'OPTIONS':
        response = jsonify({"status": "success", "message": "CORS preflight successful."})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response

    command_data = request.json
    if not command_data or 'command' not in command_data:
        return jsonify({"status": "error", "message": "No command provided."}), 400

    command = command_data['command'].strip()
    parts = command.split()
    if not parts:
        return jsonify({"status": "error", "message": "Invalid command."}), 400

    cmd = parts[0].lower()
    args = parts[1:]

    with lock:
        if cmd == "/login":
            print("Login attempted.")
            if len(args) != 2:
                return jsonify({"status": "error", "message": "Usage: /login <server_ip> <player_id>"}), 400
            
            player_ip = args[0]
            player_id = args[1]
            print(f"Login ID:{player_id}, IP: {player_ip}")

            if player_id in players:
                return jsonify({"status": "error", "message": f"Player ID '{player_id}' already connected."}), 400
            
            players[player_id] = {
                "id": player_id,
                "ip": player_ip,
                "score": 0,
                "health": 10
            }
            print(f"Adding new player...")


            # Log the login event
            logs.append(f"Player {player_id} logged in from IP {player_ip}")

            return jsonify({"status": "success", "message": f"Welcome to the Dojo, Player {player_id}!"})

        elif cmd == "/disconnect":
            if len(args) != 1:
                return jsonify({"status": "error", "message": "Usage: /disconnect <player_id>"}), 400
            
            player_id = args[0]
            if player_id not in players:
                return jsonify({"status": "error", "message": f"Player '{player_id}' not found."}), 404
            
            del players[player_id]

            # Log the disconnect event
            logs.append(f"Player {player_id} disconnected.")

            return jsonify({"status": "success", "message": f"Player {player_id} disconnected."})

        elif cmd == "/game_state":
            game_state = [
                f"Player {p['id']}: IP={p['ip']}, Score={p['score']}, Health={p['health']}"
                for p in players.values()
            ]
            return jsonify({"status": "success", "message": "\n".join(game_state) if game_state else "No players connected."})

        elif cmd == "/reset":
            players.clear()
            logs.append("Game state reset.")
            return jsonify({"status": "success", "message": "Game state reset."})

        elif cmd == "heal":
            if len(args) != 1:
                return jsonify({"status": "error", "message": "Usage: heal <player_id>"}), 400

            target_id = args[0]

            if target_id not in players:
                return jsonify({"status": "error", "message": f"Player '{target_id}' not found."}), 404

            # Heal the player (max 10 HP)
            if players[target_id]["health"] < 10:
                players[target_id]["health"] += 1
                logs.append(f"Player {target_id} was healed! Current health: {players[target_id]['health']}")

                return jsonify({"status": "success", "message": f"Player {target_id} healed! Current health: {players[target_id]['health']}"})

            else:
                return jsonify({"status": "error", "message": f"Player {target_id} is already at full health (10 HP)."})

        elif cmd == "attack":
            print(f"Received attack command. Raw input: {command_data}")  # Debugging
            print(f"Command split into parts: {parts}")  # Debugging

            if len(args) != 1:
                print("Error: attack command requires exactly 1 argument")  # Debugging
                return jsonify({"status": "error", "message": "Usage: attack <player_id>"}), 400
           
            target_id = args[0]

            if target_id not in players:
                return jsonify({"status": "error", "message": f"Player '{target_id}' not found."}), 404

            # Reduce health
            if players[target_id]["health"] > 0:
                players[target_id]["health"] -= 1
                logs.append(f"Player {target_id} was attacked! Remaining health: {players[target_id]['health']}")

                # Check if player is eliminated
                if players[target_id]["health"] <= 0:
                    logs.append(f"Player {target_id} has been eliminated!")
                    #del players[target_id]  # Remove the player from the game
                    players[target_id]["health"] = 10 # temp - reset health

                    update_health(target_id)
                    return jsonify({"status": "success", "message": f"Player {target_id} has been eliminated!"})
                update_health(target_id)
                return jsonify({"status": "success", "message": f"Player {target_id} attacked! Remaining health: {players[target_id]['health']}"})

            else:
                return jsonify({"status": "error", "message": f"Player {target_id} has already been eliminated."})
        else:
            return jsonify({"status": "error", "message": f"Unknown command: {cmd}. Use /help to see available commands."})

@app.route('/kick', methods=['POST'])
def kick_player():
    player_id = request.form.get('player_id')

    if not player_id:
        return jsonify({"status": "error", "message": "No player ID provided."}), 400

    with lock:
        if player_id not in players:
            return jsonify({"status": "error", "message": f"Player '{player_id}' not found."}), 404

        del players[player_id]

    logs.append(f"Player {player_id} has been kicked.")
    return jsonify({"status": "success", "message": f"Player {player_id} has been kicked."})

@app.route('/get_game_data', methods=['GET'])
def get_game_data():
    """Provide updated logs and connected players."""
    return jsonify({
        'players': players,
        'logs': logs
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
