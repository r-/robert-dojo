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

    if team not in ['0', '1']:  # Set teams here
        return jsonify({"status": "error", "message": f"Invalid team '{team}'."}), 400

    players[player_id]["team"] = team

    logs.append(f"Player {player_id} joined {team}.")

    return jsonify({"status": "success", "message": f"Player {player_id} has successfully joined the {team} team!"})

@dojocontrol_bp.route('/restart', methods=['POST'])
def restart():
    players = current_app.config['PLAYERS']
    logs = current_app.config['LOGS']
    score = current_app.config["SCORE"]

    for player_id, player_info in players.items():
        players[player_id]["health"] = 4
        players[player_id]["flag"] = False
        players[player_id]["deaths"] = 0
        players[player_id]["score"] = 0

    score["0"] = 0
    score["1"] = 0

    logs.append(f"Game has been reset.")
    return jsonify({"status": "success", "message": "Reset successful."})