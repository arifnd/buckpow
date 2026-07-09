from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.project_service import ProjectService

projects_bp = Blueprint('api_projects', __name__)


@projects_bp.route('/projects', methods=['GET'])
@login_required
def list_projects():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if page == 0:
        projects = ProjectService.get_all()
        return jsonify([p.to_dict() for p in projects])
    pagination = ProjectService.get_paginated(page=page, per_page=per_page)
    return jsonify({
        'projects': [p.to_dict() for p in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
    })


@projects_bp.route('/projects', methods=['POST'])
@login_required
def create_project():
    body = request.get_json()
    if not body or 'name' not in body:
        return jsonify({'error': 'name is required'}), 400

    project = ProjectService.create(
        name=body['name'],
        description=body.get('description', ''),
        owner_id=current_user.id,
    )
    return jsonify(project.to_dict()), 201


@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    project = ProjectService.get_by_id(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify(project.to_dict())


@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    body = request.get_json()
    if not body:
        return jsonify({'error': 'No JSON payload'}), 400

    project = ProjectService.update(
        project_id,
        name=body.get('name'),
        description=body.get('description'),
    )
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify(project.to_dict())


@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    if ProjectService.delete(project_id):
        return jsonify({'status': 'deleted'}), 200
    return jsonify({'error': 'Project not found'}), 404
