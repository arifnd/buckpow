from datetime import datetime, timedelta


def utc_iso(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.isoformat() + "Z"
    return dt.isoformat().replace("+00:00", "Z")


def to_utc_date_bounds(
    date_str: str, tz_offset: float = 0
) -> tuple[datetime, datetime]:
    """Convert a local date string to naive UTC start/end boundaries.

    Given a YYYY-MM-DD in the user's local timezone, returns the UTC
    bounds that cover that entire day. Both returned datetimes are
    timezone-naive (UTC) for direct comparison with SQLite stored values.

    Example (tz_offset=7, date="2026-07-11"):
        start = 2026-07-10 17:00:00  (= Jul 11 00:00 GMT+7)
        end   = 2026-07-11 16:59:59  (= Jul 11 23:59 GMT+7)
    """
    parts = date_str.split("-")
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    start = datetime(year, month, day) - timedelta(hours=tz_offset)
    end = datetime(year, month, day, 23, 59, 59) - timedelta(hours=tz_offset)
    return start, end
