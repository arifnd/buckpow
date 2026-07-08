from flask import Blueprint, request, jsonify
from app.services.device_service import DeviceService

devices_bp = Blueprint('api_devices', __name__)


@devices_bp.route('/devices', methods=['GET'])
def list_devices():
    devices = DeviceService.get_all()
    return jsonify([d.to_dict() for d in devices])


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

    device = DeviceService.update(
        device_id,
        alias=body.get('alias'),
        description=body.get('description'),
        sampling_interval=body.get('sampling_interval'),
    )
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify(device.to_dict())


@devices_bp.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    if DeviceService.delete(device_id):
        return jsonify({'status': 'deleted'}), 200
    return jsonify({'error': 'Device not found'}), 404
