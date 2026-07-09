from flask import Blueprint, jsonify

health_bp = Blueprint('api_health', __name__)


@health_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})
