from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, send_file
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

    allowed = {'high_power_threshold', 'high_current_threshold', 'low_voltage_threshold',
               'brand', 'timestamp_format', 'timezone', 'device_watchdog_timeout'}
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


@settings_bp.route('/settings/backup', methods=['GET'])
@login_required
def backup_database():
    from flask import current_app
    import os

    db_url = str(db.engine.url)
    if db_url.startswith('sqlite:///'):
        db_path = db_url[10:]
    elif db_url.startswith('sqlite://'):
        db_path = db_url[9:]
    else:
        return error_response('Backup only supported for SQLite', 400)

    if not os.path.isabs(db_path):
        db_path = os.path.join(current_app.instance_path, db_path)

    if not os.path.exists(db_path):
        return error_response('Database file not found', 404)

    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S')
    return send_file(
        db_path,
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=f'buckpow-backup-{ts}.db',
    )
