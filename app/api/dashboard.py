from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.measurement_service import MeasurementService
from app.services.device_service import DeviceService
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get('/dashboard')
def dashboard_data(db: Session = Depends(get_db)):
    measurements = MeasurementService(db).get_recent(limit=1)
    stats = MeasurementService(db).get_stats()
    devices = DeviceService(db).get_all()
    devices_data = [d.to_dict() for d in devices]
    latest = measurements[0].to_dict() if measurements else None
    return {
        'latest': latest,
        'stats': stats,
        'devices': devices_data,
    }


@router.get('/dashboard/summary')
def dashboard_summary(db: Session = Depends(get_db)):
    return DashboardService(db).get_summary()


@router.get('/dashboard/statistics')
def dashboard_statistics(
    device_id: int | None = Query(None),
    session_id: int | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return DashboardService(db).get_statistics(device_id=device_id, session_id=session_id,
        start_date=start_date, end_date=end_date,
    )
