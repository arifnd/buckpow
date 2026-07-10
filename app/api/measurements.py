import csv, io
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, Response, send_file
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from app import db
from app.services.measurement_service import MeasurementService
from app.services.device_service import DeviceService
from app.utils.errors import error_response
from app.utils.validators import validate_required
from app.api.health import MIN_FIRMWARE_VERSION

measurements_bp = Blueprint('api_measurements', __name__)


def _parse_version(v):
    try:
        return tuple(int(x) for x in v.split('.'))
    except (ValueError, AttributeError):
        return None


def require_device_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return error_response('Missing or invalid Authorization header', 401)
        api_key = auth[7:]
        device = DeviceService.get_by_api_key(api_key)
        if not device:
            return error_response('Invalid API key', 401)
        if not device.enabled:
            return error_response('Device is disabled', 403)
        request.device = device
        return f(*args, **kwargs)
    return decorated


@measurements_bp.route('/measurements', methods=['POST'])
@require_device_api_key
def receive_measurement():
    body = request.get_json()
    if not body:
        return error_response('No JSON payload', 400)

    required = ['device_id', 'bus_voltage', 'shunt_voltage', 'current', 'power']
    missing = validate_required(body, required)
    if missing:
        return error_response(f'Missing field: {missing}', 400)

    device_id_str = body['device_id']
    if device_id_str != request.device.device_id:
        return error_response('device_id does not match the authenticated device', 403)

    fw = body.get('firmware_version', '')
    device = request.device
    outdated = False
    if fw:
        parsed = _parse_version(fw)
        min_fw = _parse_version(MIN_FIRMWARE_VERSION)
        if parsed and min_fw and parsed < min_fw:
            outdated = True
        if fw != device.firmware_version:
            device.firmware_version = fw
            db.session.commit()
    elif not device.firmware_version:
        device.firmware_version = 'unknown'
        db.session.commit()

    try:
        measurement = MeasurementService.create(
            device_id_str=device_id_str,
            bus_voltage=float(body['bus_voltage']),
            shunt_voltage=float(body['shunt_voltage']),
            current=float(body['current']),
            power=float(body['power']),
        )
        resp = jsonify({'status': 'success', 'id': measurement.id})
        if outdated:
            resp.headers['X-Firmware-Outdated'] = 'true'
        return resp, 201
    except Exception as e:
        return error_response(str(e), 500)


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


@measurements_bp.route('/measurements/export/xlsx', methods=['GET'])
def export_xlsx():
    device_id = request.args.get('device_id', type=int)
    session_id = request.args.get('session_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    rows = MeasurementService.get_all_filtered(
        device_id=device_id, session_id=session_id,
        start_date=start_date, end_date=end_date
    )

    wb = Workbook()
    ws = wb.active
    ws.title = 'Measurements'

    headers = ['ID', 'Device', 'Session', 'Bus Voltage', 'Shunt Voltage', 'Load Voltage', 'Current (A)', 'Power (W)', 'Energy (Wh)', 'Timestamp']
    bold = Font(bold=True)
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = bold

    for i, m in enumerate(rows, 2):
        ws.cell(row=i, column=1, value=m.id)
        ws.cell(row=i, column=2, value=m.device.device_id if m.device else '')
        ws.cell(row=i, column=3, value=m.session.name if m.session else '')
        ws.cell(row=i, column=4, value=m.bus_voltage)
        ws.cell(row=i, column=5, value=m.shunt_voltage)
        ws.cell(row=i, column=6, value=m.load_voltage)
        ws.cell(row=i, column=7, value=m.current)
        ws.cell(row=i, column=8, value=m.power)
        ws.cell(row=i, column=9, value=m.energy)
        ws.cell(row=i, column=10, value=m.created_at.isoformat() if m.created_at else '')

    for col in range(1, len(headers) + 1):
        max_len = 0
        for row in ws.iter_rows(min_col=col, max_col=col, values_only=True):
            val = str(row[0] or '')
            max_len = max(max_len, len(val))
        ws.column_dimensions[get_column_letter(col)].width = max_len + 3

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='measurements.xlsx',
    )


@measurements_bp.route('/chart', methods=['GET'])
def chart_data():
    device_id = request.args.get('device_id', type=int)
    session_id = request.args.get('session_id', type=int)
    limit = request.args.get('limit', 500, type=int)
    granularity = request.args.get('granularity')
    time_range = request.args.get('range')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if granularity not in (None, 's', 'm', 'h', 'd'):
        granularity = None

    if time_range == '1h':
        start_date = datetime.now(timezone.utc) - timedelta(hours=1)
    elif time_range == '24h':
        start_date = datetime.now(timezone.utc) - timedelta(hours=24)
    elif time_range == '7d':
        start_date = datetime.now(timezone.utc) - timedelta(days=7)
    elif time_range == '30d':
        start_date = datetime.now(timezone.utc) - timedelta(days=30)

    data = MeasurementService.get_chart_data(
        limit=limit, device_id=device_id, session_id=session_id,
        granularity=granularity, start_date=start_date, end_date=end_date,
    )
    return jsonify(data)
