from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.measurement_service import MeasurementService
from app.auth import require_user

router = APIRouter()


@router.get('/benchmark/compare')
def compare(
    sessions: str = Query(''),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_user),
):
    if not sessions:
        raise HTTPException(status_code=400, detail='sessions parameter is required (comma-separated IDs)')
    session_ids = [s.strip() for s in sessions.split(',') if s.strip()]
    if len(session_ids) < 2:
        raise HTTPException(status_code=400, detail='At least two session IDs are required')
    results = []
    for sid in session_ids:
        try:
            sid_int = int(sid)
        except ValueError:
            continue
        stats = MeasurementService.get_session_stats(db, sid_int)
        if stats:
            results.append(stats)
    if len(results) < 2:
        raise HTTPException(status_code=404, detail='Could not find at least two valid sessions')
    return {'sessions': results}
