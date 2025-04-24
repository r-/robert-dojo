from flask import Flask, jsonify, request, render_template, send_file, Blueprint
import threading
lock = threading.Lock()

app = Flask(__name__)
dojocontrol_bp = Blueprint('dojocontrol_bp', __name__)

@dojocontrol_bp.route('/kick', methods=['POST'])
def kick_player():
    player_id = request.form.get('player_id')

    if not player_id:
        return jsonify({"status": "error", "message": "No player ID provided."}), 400

    with lock:
        if player_id not in app.players:
            return jsonify({"status": "error", "message": f"Player '{player_id}' not found."}), 404

        del app.players[player_id]

    app.logs.append(f"Player {player_id} has been kicked.")
    return jsonify({"status": "success", "message": f"Player {player_id} has been kicked."})