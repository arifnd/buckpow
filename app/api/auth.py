from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.services.user_service import UserService

auth_bp = Blueprint('api_auth', __name__)


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'No JSON payload'}), 400

    email = body.get('email', '').strip()
    password = body.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = UserService.authenticate(email, password)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    login_user(user)
    return jsonify({'status': 'ok', 'user': user.to_dict()})


@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'status': 'ok'})


@auth_bp.route('/auth/profile', methods=['PUT'])
@login_required
def update_profile():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'No JSON payload'}), 400
    try:
        user = UserService.update(
            current_user.id,
            name=body.get('name'),
            email=body.get('email'),
            password=body.get('password') or None,
        )
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'status': 'ok', 'user': user.to_dict()})
    except ValueError as e:
        return jsonify({'error': str(e)}), 409


@auth_bp.route('/auth/me', methods=['GET'])
def me():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(current_user.to_dict())
