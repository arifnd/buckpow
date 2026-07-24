from fastapi import APIRouter, Query, HTTPException

from src.measurements.service import MeasurementService
from src.dependencies import DbDep, RequiredUserDep

router = APIRouter()


def _parse_session_ids(sessions: str) -> list[int]:
    if not sessions:
        raise HTTPException(
            status_code=400,
            detail="sessions parameter is required (comma-separated IDs)",
        )
    ids = []
    for s in sessions.split(","):
        s = s.strip()
        if not s:
            continue
        try:
            ids.append(int(s))
        except ValueError:
            continue
    if len(ids) < 2 or len(ids) > 3:
        raise HTTPException(status_code=400, detail="2 to 3 session IDs are required")
    return ids


@router.get("/benchmark/compare")
def compare(
    db: DbDep,
    _current_user: RequiredUserDep,
    sessions: str = Query(""),
):
    session_ids = _parse_session_ids(sessions)
    svc = MeasurementService(db)
    results = []
    for sid in session_ids:
        stat = svc.get_session_stats(db, sid)
        if not stat:
            continue
        chart = svc.get_chart_data(session_id=sid)
        stat["chart_data"] = {
            "labels": chart.get("labels", []),
            "power": chart.get("power", []),
        }
        results.append(stat)
    if len(results) < 2:
        raise HTTPException(
            status_code=404, detail="Could not find at least two valid sessions"
        )
    return {"sessions": results}
