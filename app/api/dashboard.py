from flask import Blueprint, jsonify, request
from app.services.measurement_service import MeasurementService
from app.services.device_service import DeviceService
from app.services.session_service import SessionService
from app.services.dashboard_service import DashboardService

dashboard_bp = Blueprint('api_dashboard', __name__)


@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard_data():
    device_id = request.args.get('device_id', type=int)
    measurements = MeasurementService.get_recent(limit=1, device_id=device_id)
    stats = MeasurementService.get_stats(device_id=device_id)

    devices = DeviceService.get_all()
    devices_data = [d.to_dict() for d in devices]

    latest = measurements[0].to_dict() if measurements else None
    active_session = SessionService.get_any_active_session()

    return jsonify({
        'latest': latest,
        'stats': stats,
        'devices': devices_data,
        'active_session': active_session.to_dict() if active_session else None,
    })


@dashboard_bp.route('/dashboard/summary', methods=['GET'])
def dashboard_summary():
    return jsonify(DashboardService.get_summary())


@dashboard_bp.route('/dashboard/statistics', methods=['GET'])
def dashboard_statistics():
    device_id = request.args.get('device_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = DashboardService.get_statistics(
        device_id=device_id, start_date=start_date, end_date=end_date
    )
    return jsonify(data)
