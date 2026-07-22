from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.auth.models import User
from src.dependencies import require_user
from src.measurements.service import MeasurementService
from src.devices.service import DeviceService
from src.dashboard.service import DashboardService

router = APIRouter()


@router.get("/dashboard")
def dashboard_data(
    db: Session = Depends(get_db), _current_user: User = Depends(require_user)
):
    measurements = MeasurementService(db).get_recent(limit=1)
    stats = MeasurementService(db).get_stats()
    devices = DeviceService(db).get_all()
    devices_data = [d.to_dict() for d in devices]
    latest = measurements[0].to_dict() if measurements else None
    return {"latest": latest, "stats": stats, "devices": devices_data}


@router.get("/dashboard/summary")
def dashboard_summary(
    db: Session = Depends(get_db), _current_user: User = Depends(require_user)
):
    return DashboardService(db).get_summary()


@router.get("/dashboard/statistics")
def dashboard_statistics(
    device_id: int | None = Query(None),
    session_id: int | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_user),
):
    return DashboardService(db).get_statistics(
        device_id=device_id,
        session_id=session_id,
        start_date=start_date,
        end_date=end_date,
    )
