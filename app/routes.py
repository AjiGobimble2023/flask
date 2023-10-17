from flask import Blueprint, jsonify, request
from .user.controller import  process_json

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return 'Welcome to IRT Test!'

bp.route('/process_json', methods=['POST'])(process_json)