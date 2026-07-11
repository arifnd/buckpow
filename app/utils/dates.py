def utc_iso(dt):
    if dt is None:
        return None
    return dt.isoformat().replace('+00:00', 'Z')
