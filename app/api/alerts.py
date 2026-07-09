from flask import Blueprint, request, jsonify
from app.services.alert_service import AlertService

alerts_bp = Blueprint('api_alerts', __name__)


@alerts_bp.route('/alerts', methods=['GET'])
def list_alerts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    device_id = request.args.get('device_id', type=int)
    level = request.args.get('level')
    resolved = request.args.get('resolved')
    if resolved is not None:
        resolved = resolved.lower() in ('true', '1')
    pagination = AlertService.get_paginated(
        page=page, per_page=per_page,
        device_id=device_id, level=level, resolved=resolved,
    )
    return jsonify({
        'alerts': [a.to_dict() for a in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
        'unresolved_count': AlertService.get_unresolved_count(),
    })


@alerts_bp.route('/alerts', methods=['POST'])
def create_alert():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'No JSON payload'}), 400
    device_id = body.get('device_id')
    level = body.get('level', 'warning')
    message = body.get('message', '')
    if not device_id or not message:
        return jsonify({'error': 'device_id and message are required'}), 400
    alert = AlertService.create(device_id, level, message)
    return jsonify(alert.to_dict()), 201


@alerts_bp.route('/alerts/<int:alert_id>/resolve', methods=['PATCH'])
def resolve_alert(alert_id):
    alert = AlertService.resolve(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    return jsonify(alert.to_dict())


@alerts_bp.route('/alerts/resolve-all', methods=['POST'])
def resolve_all():
    device_id = request.args.get('device_id', type=int)
    AlertService.resolve_all(device_id=device_id)
    return jsonify({'status': 'ok'})
