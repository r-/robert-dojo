from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

players = {}
lock = threading.Lock()

@app.route('/command', methods=['OPTIONS', 'POST'])
def command():
    """
    Unified command handler for game server interactions.
    Handles commands like /login, /disconnect, /shoot, /game_state, /reset.
    """
    if request.method == 'OPTIONS':
        # Handle CORS preflight
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
            if len(args) != 2:
                return jsonify({"status": "error", "message": "Usage: /login <server_ip> <player_id>"}), 400
            
            player_id = args[1]
            player_ip = request.remote_addr
            if player_id in players:
                return jsonify({"status": "error", "message": f"Player ID '{player_id}' already connected."}), 400
            
            players[player_id] = {
                "id": player_id,
                "ip": player_ip,
                "score": 0,
                "health": 4
            }
            welcome_message = f"""
Welcome to the Dojo, Player {player_id}!
You can use the following commands to interact with the game:
- /help: View all available commands.
- /game_state: Check the current game state.
- /disconnect: Disconnect from the game.
Have fun!
"""
            return jsonify({"status": "success", "message": welcome_message.strip()})

        elif cmd == "/disconnect":
            if len(args) != 1:
                return jsonify({"status": "error", "message": "Usage: /disconnect <player_id>"}), 400
            
            player_id = args[0]
            if player_id not in players:
                return jsonify({"status": "error", "message": f"Player '{player_id}' not found."}), 404
            
            del players[player_id]
            return jsonify({"status": "success", "message": f"Player {player_id} disconnected."})

        elif cmd == "/shoot":
            if len(args) != 2:
                return jsonify({"status": "error", "message": "Usage: /shoot <shooter_id> <target_id>"}), 400
            
            shooter_id, target_id = args
            if shooter_id not in players or target_id not in players:
                return jsonify({"status": "error", "message": "Shooter or target not found."}), 404
            
            if players[target_id]['health'] > 0:
                players[target_id]['health'] -= 1
                if players[target_id]['health'] == 0:
                    players[shooter_id]['score'] += 1
                    return jsonify({
                        "status": "success",
                        "message": f"Player {target_id} eliminated by {shooter_id}.",
                        "players": list(players.values())
                    })
            return jsonify({
                "status": "success",
                "message": f"Player {shooter_id} shot {target_id}.",
                "players": list(players.values())
            })

        elif cmd == "/game_state":
            game_state = [
                f"Player {p['id']}: IP={p['ip']}, Score={p['score']}, Health={p['health']}"
                for p in players.values()
            ]
            return jsonify({"status": "success", "message": "\n".join(game_state) if game_state else "No players connected."})

        elif cmd == "/reset":
            players.clear()
            return jsonify({"status": "success", "message": "Game state reset."})

        elif cmd == "/help":
            help_text = """
Available Commands:
  /login <server_ip> <player_id> - Log in to the game.
  /disconnect <player_id> - Disconnect from the game.
  /shoot <shooter_id> <target_id> - Shoot another player.
  /game_state - View the current game state.
  /reset - Reset the game state.
  /help - Display this help text.
"""
            return jsonify({"status": "success", "message": help_text.strip()})

        else:
            return jsonify({"status": "error", "message": f"Unknown command: {cmd}. Use /help to see available commands."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
