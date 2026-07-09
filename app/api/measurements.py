import csv, io
from functools import wraps
from flask import Blueprint, request, jsonify, Response
from app.services.measurement_service import MeasurementService
from app.services.device_service import DeviceService

measurements_bp = Blueprint('api_measurements', __name__)


def require_device_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        api_key = auth[7:]
        device = DeviceService.get_by_api_key(api_key)
        if not device:
            return jsonify({'error': 'Invalid API key'}), 401
        if not device.enabled:
            return jsonify({'error': 'Device is disabled'}), 403
        request.device = device
        return f(*args, **kwargs)
    return decorated


@measurements_bp.route('/measurements', methods=['POST'])
@require_device_api_key
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
    session_id = request.args.get('session_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    pagination = MeasurementService.get_paginated(
        page=page, per_page=per_page,
        device_id=device_id, session_id=session_id,
        start_date=start_date, end_date=end_date
    )

    return jsonify({
        'measurements': [m.to_dict() for m in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
    })


@measurements_bp.route('/measurements/export/csv', methods=['GET'])
def export_csv():
    device_id = request.args.get('device_id', type=int)
    session_id = request.args.get('session_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    rows = MeasurementService.get_all_filtered(
        device_id=device_id, session_id=session_id,
        start_date=start_date, end_date=end_date
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Device', 'Session', 'Bus Voltage', 'Shunt Voltage', 'Load Voltage', 'Current (A)', 'Power (W)', 'Energy (Wh)', 'Timestamp'])
    for m in rows:
        writer.writerow([
            m.id,
            m.device.device_id if m.device else '',
            m.session.name if m.session else '',
            m.bus_voltage, m.shunt_voltage, m.load_voltage,
            m.current, m.power, m.energy,
            m.created_at.isoformat() if m.created_at else '',
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=measurements.csv'}
    )


@measurements_bp.route('/chart', methods=['GET'])
def chart_data():
    device_id = request.args.get('device_id', type=int)
    session_id = request.args.get('session_id', type=int)
    limit = request.args.get('limit', 100, type=int)
    granularity = request.args.get('granularity')

    if granularity not in (None, 's', 'm', 'h'):
        granularity = None

    data = MeasurementService.get_chart_data(
        limit=limit, device_id=device_id, session_id=session_id,
        granularity=granularity,
    )
    return jsonify(data)
