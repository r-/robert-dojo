from flask import Flask, jsonify, request, render_template, send_file, Blueprint, current_app
import threading
lock = threading.Lock()

dojocontrol_bp = Blueprint('dojocontrol_bp', __name__)

@dojocontrol_bp.route('/kick', methods=['POST'])
def kick_player():
    players = current_app.config['PLAYERS']
    logs = current_app.config['LOGS']

    player_id = request.form.get('player_id')

    if not player_id:
        return jsonify({"status": "error", "message": "No player ID provided."}), 400

    with lock:
        if player_id not in players:
            return jsonify({"status": "error", "message": f"Player '{player_id}' not found."}), 404

        del players[player_id]

    logs.append(f"Player {player_id} has been kicked.")
    return jsonify({"status": "success", "message": f"Player {player_id} has been kicked."})
from flask import request, jsonify, current_app

@dojocontrol_bp.route('/newTeam', methods=['POST'])
def new_team():
    players = current_app.config['PLAYERS']
    logs = current_app.config['LOGS'] 

    player_id = request.form.get('player_id')
    team = request.form.get('player_team')

    if player_id not in players:
        return jsonify({"status": "error", "message": f"Player {player_id} not found."}), 404

    if team not in ["Blue", "Red"]:  # Set teams here
        return jsonify({"status": "error", "message": f"Invalid team '{team}'."}), 400

    players[player_id]["team"] = team

    logs.append(f"Player {player_id} joined {team}.")

    return jsonify({"status": "success", "message": f"Player {player_id} has successfully joined the {team} team!"})
