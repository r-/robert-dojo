import cv2
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, send_file, jsonify, Blueprint, request, current_app
import cv2.aruco as aruco
from io import BytesIO
import hashlib
from pyzbar.pyzbar import decode

qrcode_bp = Blueprint('qrcode_bp', __name__)


ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

@qrcode_bp.route('/generate_qrcodes', methods=['GET'])
def get_aruco_markers():
    """Generate and return a single image with multiple ArUco markers arranged in a grid with margins and text above each marker."""
    try:
        marker_size = 200  # Size of the marker image in pixels
        markers_per_row = 3  # Number of markers per row in the grid
        margin = 30  # Margin between markers
        text_margin = 10  # Margin between text and marker

        # List of marker IDs: Blue flag (0), Red flag (1), Players (rest)
        marker_ids = list(range(0, 8))

        # Calculate the size of the canvas based on the number of markers and their layout
        rows = len(marker_ids) // markers_per_row + (1 if len(marker_ids) % markers_per_row != 0 else 0)
        canvas_width = markers_per_row * marker_size + (markers_per_row - 1) * margin
        canvas_height = rows * (marker_size + margin) + text_margin + 100  # Space for text above the first row

        # Create a blank canvas (white background)
        canvas = np.ones((canvas_height, canvas_width), dtype=np.uint8) * 255  # white background

        # Loop through the marker IDs and generate the markers
        for idx, marker_id in enumerate(marker_ids):
            # Calculate the position (x, y) for placing the marker in the grid
            row = idx // markers_per_row
            col = idx % markers_per_row
            x_offset = col * (marker_size + margin)
            y_offset = row * (marker_size + margin) + text_margin + 50  # 50px margin before the first row of markers

            # Create the marker image
            marker_img = np.ones((marker_size, marker_size), dtype=np.uint8) * 255  # white background
            cv2.aruco.generateImageMarker(ARUCO_DICT, marker_id, marker_size, marker_img)  # Draw the marker

            # Place the marker image onto the canvas
            canvas[y_offset:y_offset + marker_size, x_offset:x_offset + marker_size] = marker_img

            # Add the label text above the marker
            if marker_id == 0:
                label_text = f"Blue Flag"
            elif marker_id == 1:
                label_text = f"Red Flag"
            else:
                label_text = f"ID: {marker_id}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 1
            text_size = cv2.getTextSize(label_text, font, font_scale, font_thickness)[0]
            text_x = x_offset + (marker_size - text_size[0]) // 2  # Center the text horizontally
            text_y = y_offset - text_margin  # Position the text above the marker

            # Draw the label text above the marker
            cv2.putText(canvas, label_text, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness, cv2.LINE_AA)

        # Encode the combined image to PNG in memory
        is_success, buffer = cv2.imencode(".png", canvas)
        if not is_success:
            raise ValueError("Failed to encode the combined ArUco markers image.")

        # Convert the image buffer to a byte stream
        img_io = BytesIO(buffer.tobytes())

        # Return the image
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        qrcode_bp.logger.error(f"Error generating ArUco markers: {e}")
        return jsonify({"status": "error", "message": "Failed to generate ArUco markers."}), 500
    
@qrcode_bp.route('/decode_qr_code', methods=['POST'])
def decode_qr_code():
    players = current_app.config['PLAYERS']

    """Receive a QR code image, decode it, and return the player type."""
    try:
        # Check if the request contains a file
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part."}), 400
        
        file = request.files['file']
        
        # If no file is selected
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file."}), 400
        
        # Open the image and decode the QR code
        img = Image.open(file.stream)
        decoded_objects = decode(img)

        if not decoded_objects:
            return jsonify({"status": "error", "message": "No QR code found in the image."}), 400

        # Get the player ID from the QR code (assuming the QR code contains player_id as URL)
        player_id = decoded_objects[0].data.decode('utf-8').split('/')[-1]  # Extract player_id from URL
        
        # Check if the player exists
        if player_id not in players:
            return jsonify({"status": "error", "message": f"Player '{player_id}' not found."}), 404
        
        # Return the player type
        player_type = players[player_id]["type"]
        return jsonify({"status": "success", "player_id": player_id, "player_type": player_type})

    except Exception as e:
        # Handle errors
        qrcode_bp.logger.error(f"Error decoding QR code: {e}")
        return jsonify({"status": "error", "message": "Failed to decode QR code."}), 500
    
@qrcode_bp.route('/get_qr_code/<player_id>', methods=['GET'])
def get_aruco_marker(player_id):
    players = current_app.config['PLAYERS']
    """Generate and return an ArUco marker for the given player ID."""
    try:
        if player_id not in players:
            qrcode_bp.logger.error(f"Player '{player_id}' not found.")
            return jsonify({"status": "error", "message": f"Player '{player_id}' not found."}), 404

        if not player_id.isdigit(): 
            marker_id = int(hashlib.md5(player_id.encode('utf-8')).hexdigest(), 16) % 50
        else:
            marker_id = int(player_id) % 50  # assuming DICT_4X4_50 (valid IDs: 0-49)

        marker_size = 300  # Size of the marker image in pixels

        # Create the ArUco marker using cv2.aruco and manual image creation
        marker_img = np.ones((marker_size, marker_size), dtype=np.uint8) * 255  # white background
        cv2.aruco.generateImageMarker(ARUCO_DICT, marker_id, marker_size, marker_img)  # Draw the marker

        # Encode the image to PNG in memory
        is_success, buffer = cv2.imencode(".png", marker_img)
        if not is_success:
            raise ValueError("Failed to encode ArUco marker image.")

        img_io = BytesIO(buffer.tobytes())

        # Return the image
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        qrcode_bp.logger.error(f"Error generating ArUco marker for player {player_id}: {e}")
        return jsonify({"status": "error", "message": "Failed to generate ArUco marker."}), 500
