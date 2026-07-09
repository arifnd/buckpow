from flask import Blueprint, request, jsonify
from app.services.session_service import SessionService

sessions_bp = Blueprint('api_sessions', __name__)


@sessions_bp.route('/sessions', methods=['GET'])
def list_sessions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if page == 0:
        sessions = SessionService.get_all()
        return jsonify([s.to_dict() for s in sessions])
    pagination = SessionService.get_paginated(page=page, per_page=per_page)
    return jsonify({
        'sessions': [s.to_dict() for s in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
    })


@sessions_bp.route('/sessions', methods=['POST'])
def create_session():
    body = request.get_json()
    if not body or 'name' not in body or 'device_id' not in body:
        return jsonify({'error': 'name and device_id are required'}), 400

    session = SessionService.create(
        device_id=body['device_id'],
        name=body['name'],
        target_device=body.get('target_device', ''),
        description=body.get('description', ''),
        project_id=body.get('project_id'),
    )
    return jsonify(session.to_dict()), 201


@sessions_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    session = SessionService.get_by_id(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(session.to_dict())


@sessions_bp.route('/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    body = request.get_json()
    if not body:
        return jsonify({'error': 'No JSON payload'}), 400

    session = SessionService.update(
        session_id,
        name=body.get('name'),
        target_device=body.get('target_device'),
        description=body.get('description'),
        project_id=body.get('project_id'),
    )
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(session.to_dict())


@sessions_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    if SessionService.delete(session_id):
        return jsonify({'status': 'deleted'}), 200
    return jsonify({'error': 'Session not found'}), 404


@sessions_bp.route('/sessions/<int:session_id>/start', methods=['POST'])
def start_session(session_id):
    session, error = SessionService.start(session_id)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(session.to_dict())


@sessions_bp.route('/sessions/<int:session_id>/stop', methods=['POST'])
def stop_session(session_id):
    session, error = SessionService.stop(session_id)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(session.to_dict())
