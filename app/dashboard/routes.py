from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@dashboard_bp.route('/')
def index():
    return render_template('dashboard/index.html', active_page='dashboard')


@dashboard_bp.route('/devices')
def devices():
    return render_template('devices/index.html', active_page='devices')


@dashboard_bp.route('/devices/new')
def devices_new():
    return render_template('devices/form.html', active_page='devices', device=None)


@dashboard_bp.route('/devices/<int:device_id>/edit')
def devices_edit(device_id):
    from app.services.device_service import DeviceService
    device = DeviceService.get_by_id(device_id)
    return render_template('devices/form.html', active_page='devices', device=device)


@dashboard_bp.route('/sessions')
def sessions():
    return render_template('sessions/index.html', active_page='sessions')


@dashboard_bp.route('/sessions/new')
def sessions_new():
    from app.services.device_service import DeviceService
    devices = DeviceService.get_all()
    return render_template('sessions/form.html', active_page='sessions', session=None, devices=devices)


@dashboard_bp.route('/sessions/<int:session_id>/edit')
def sessions_edit(session_id):
    from app.services.session_service import SessionService
    from app.services.device_service import DeviceService
    session = SessionService.get_by_id(session_id)
    devices = DeviceService.get_all()
    return render_template('sessions/form.html', active_page='sessions', session=session, devices=devices)


@dashboard_bp.route('/measurements')
def measurements():
    return render_template('measurements/index.html', active_page='measurements')
