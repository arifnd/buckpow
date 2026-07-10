from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from app.services.user_service import UserService

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@dashboard_bp.route('/auth/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    return render_template('auth/login.html')


@dashboard_bp.route('/auth/logout', methods=['POST'])
def logout():
    logout_user()
    return {'status': 'ok'}


@dashboard_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', active_page='dashboard')


@dashboard_bp.route('/devices')
@login_required
def devices():
    return render_template('devices/index.html', active_page='devices')


@dashboard_bp.route('/devices/new')
@login_required
def devices_new():
    from app.services.project_service import ProjectService
    projects = ProjectService.get_all()
    return render_template('devices/form.html', active_page='devices', device=None, projects=projects)


@dashboard_bp.route('/devices/<int:device_id>/edit')
@login_required
def devices_edit(device_id):
    from app.services.device_service import DeviceService
    from app.services.project_service import ProjectService
    device = DeviceService.get_by_id(device_id)
    projects = ProjectService.get_all()
    return render_template('devices/form.html', active_page='devices', device=device, projects=projects)


@dashboard_bp.route('/sessions')
@login_required
def sessions():
    return render_template('sessions/index.html', active_page='sessions')


@dashboard_bp.route('/sessions/new')
@login_required
def sessions_new():
    from app.services.device_service import DeviceService
    from app.services.session_service import SessionService
    from app.services.project_service import ProjectService
    devices = [d for d in DeviceService.get_all() if not SessionService.get_active_session(d.id)]
    projects = ProjectService.get_all()
    return render_template('sessions/form.html', active_page='sessions', session=None, devices=devices, projects=projects)


@dashboard_bp.route('/sessions/<int:session_id>/edit')
@login_required
def sessions_edit(session_id):
    from app.services.session_service import SessionService
    from app.services.device_service import DeviceService
    from app.services.project_service import ProjectService
    session = SessionService.get_by_id(session_id)
    devices = DeviceService.get_all()
    projects = ProjectService.get_all()
    return render_template('sessions/form.html', active_page='sessions', session=session, devices=devices, projects=projects)


@dashboard_bp.route('/projects')
@login_required
def projects():
    return render_template('projects/index.html', active_page='projects')


@dashboard_bp.route('/measurements')
@login_required
def measurements():
    return render_template('measurements/index.html', active_page='measurements')


@dashboard_bp.route('/benchmark')
@login_required
def benchmark():
    return render_template('benchmark/index.html', active_page='benchmark')


@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', active_page='profile')


@dashboard_bp.route('/alerts')
@login_required
def alerts():
    return render_template('alerts/index.html', active_page='alerts')


@dashboard_bp.route('/settings')
@login_required
def settings():
    return render_template('settings/index.html', active_page='settings')
