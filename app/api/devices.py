from flask import Blueprint, request, jsonify
from app import db
from app.models import Device
from app.services.device_service import DeviceService


devices_bp = Blueprint('api_devices', __name__)


@devices_bp.route('/devices', methods=['GET'])
def list_devices():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if page == 0:
        devices = DeviceService.get_all()
        return jsonify([d.to_dict() for d in devices])
    pagination = DeviceService.get_paginated(page=page, per_page=per_page)
    return jsonify({
        'devices': [d.to_dict() for d in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
    })


@devices_bp.route('/devices', methods=['POST'])
def create_device():
    body = request.get_json()
    if not body or 'device_id' not in body:
        return jsonify({'error': 'device_id is required'}), 400

    device = DeviceService.create(
        device_id=body['device_id'],
        alias=body.get('alias', ''),
        description=body.get('description', ''),
        sampling_interval=body.get('sampling_interval'),
        project_id=body.get('project_id'),
        firmware_version=body.get('firmware_version', ''),
    )
    return jsonify(device.to_dict()), 201


@devices_bp.route('/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    device = DeviceService.get_by_id(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify(device.to_dict())


@devices_bp.route('/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    body = request.get_json()
    if not body:
        return jsonify({'error': 'No JSON payload'}), 400

    kwargs = {}
    for key in ('alias', 'description', 'sampling_interval', 'project_id', 'firmware_version'):
        if key in body:
            kwargs[key] = body[key]
    if 'enabled' in body:
        kwargs['enabled'] = body['enabled']
    device = DeviceService.update(device_id, **kwargs)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify(device.to_dict())


@devices_bp.route('/devices/<int:device_id>/key', methods=['GET'])
def get_device_key(device_id):
    device = db.session.get(Device, device_id)
    if not device or not device.api_key:
        return jsonify({'error': 'Device not found or no API key'}), 404
    return jsonify({'api_key': device.api_key, 'id': device.id}), 200


@devices_bp.route('/devices/<int:device_id>/toggle', methods=['PATCH'])
def toggle_device(device_id):
    device = DeviceService.toggle_enabled(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify(device.to_dict()), 200


@devices_bp.route('/devices/<int:device_id>/regenerate-key', methods=['POST'])
def regenerate_key(device_id):
    device = DeviceService.regenerate_api_key(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify({'api_key': device.api_key, 'id': device.id}), 200


@devices_bp.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    if DeviceService.delete(device_id):
        return jsonify({'status': 'deleted'}), 200
    return jsonify({'error': 'Device not found'}), 404
