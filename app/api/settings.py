from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.utils.errors import error_response

settings_bp = Blueprint('api_settings', __name__)


@settings_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    return jsonify(current_user.settings or {})


@settings_bp.route('/settings', methods=['PUT'])
@login_required
def update_settings():
    body = request.get_json()
    if not body:
        return error_response('No JSON payload', 400)

    allowed = {'high_power_threshold', 'high_current_threshold', 'low_voltage_threshold', 'brand'}
    current = dict(current_user.settings or {})

    for key, value in body.items():
        if key in allowed:
            if value == '' or value is None:
                current.pop(key, None)
            else:
                current[key] = value

    current_user.settings = current
    db.session.commit()
    return jsonify(current)
