from flask import Blueprint, request, jsonify
from app.services.measurement_service import MeasurementService

measurements_bp = Blueprint('api_measurements', __name__)


@measurements_bp.route('/measurements', methods=['POST'])
def receive_measurement():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'No JSON payload'}), 400

    required = ['device_id', 'bus_voltage', 'shunt_voltage', 'current', 'power']
    for field in required:
        if field not in body:
            return jsonify({'error': f'Missing field: {field}'}), 400

    try:
        measurement = MeasurementService.create(
            device_id_str=body['device_id'],
            bus_voltage=float(body['bus_voltage']),
            shunt_voltage=float(body['shunt_voltage']),
            current=float(body['current']),
            power=float(body['power']),
        )
        return jsonify({'status': 'success', 'id': measurement.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@measurements_bp.route('/measurements', methods=['GET'])
def get_measurements():
    device_id = request.args.get('device_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    pagination = MeasurementService.get_paginated(
        page=page, per_page=per_page,
        device_id=device_id,
        start_date=start_date, end_date=end_date
    )

    return jsonify({
        'measurements': [m.to_dict() for m in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
    })


@measurements_bp.route('/chart', methods=['GET'])
def chart_data():
    device_id = request.args.get('device_id', type=int)
    session_id = request.args.get('session_id', type=int)
    limit = request.args.get('limit', 100, type=int)

    data = MeasurementService.get_chart_data(
        limit=limit, device_id=device_id, session_id=session_id
    )
    return jsonify(data)
