from flask import Blueprint, jsonify

health_bp = Blueprint('api_health', __name__)

MIN_FIRMWARE_VERSION = '1.0.0'


@health_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'min_firmware_version': MIN_FIRMWARE_VERSION})
