from flask import Flask, jsonify, request, render_template, send_file, Blueprint
import threading
lock = threading.Lock()

app = Flask(__name__)

test_bp = Blueprint('test_bp', __name__)