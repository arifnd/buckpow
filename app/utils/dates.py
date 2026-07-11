def utc_iso(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.isoformat() + 'Z'
    return dt.isoformat().replace('+00:00', 'Z')
