from flask import Blueprint, request, jsonify
from app.services.measurement_service import MeasurementService

benchmark_bp = Blueprint('api_benchmark', __name__)


@benchmark_bp.route('/benchmark/compare', methods=['GET'])
def compare():
    sessions_param = request.args.get('sessions', '')
    if not sessions_param:
        return jsonify({'error': 'sessions parameter is required (comma-separated IDs)'}), 400

    session_ids = [s.strip() for s in sessions_param.split(',') if s.strip()]
    if len(session_ids) < 2:
        return jsonify({'error': 'At least two session IDs are required'}), 400

    results = []
    for sid in session_ids:
        try:
            sid_int = int(sid)
        except ValueError:
            continue
        stats = MeasurementService.get_session_stats(sid_int)
        if stats:
            results.append(stats)

    if len(results) < 2:
        return jsonify({'error': 'Could not find at least two valid sessions'}), 404

    return jsonify({'sessions': results})
