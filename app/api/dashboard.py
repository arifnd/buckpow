from flask import Blueprint, jsonify, request
from app.services.measurement_service import MeasurementService
from app.services.device_service import DeviceService
from app.services.session_service import SessionService
from app.models import Device

dashboard_bp = Blueprint('api_dashboard', __name__)


@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard_data():
    device_id = request.args.get('device_id', type=int)
    measurements = MeasurementService.get_recent(limit=1, device_id=device_id)
    stats = MeasurementService.get_stats(device_id=device_id)

    devices = DeviceService.get_all()
    devices_data = []
    for d in devices:
        d_dict = d.to_dict()
        d_dict['status'] = DeviceService.get_online_status(d)
        devices_data.append(d_dict)

    latest = measurements[0].to_dict() if measurements else None
    active_session = SessionService.get_any_active_session()

    return jsonify({
        'latest': latest,
        'stats': stats,
        'devices': devices_data,
        'active_session': active_session.to_dict() if active_session else None,
    })
