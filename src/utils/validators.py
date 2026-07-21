import re

from .errors import ValidationError


def validate_required(body, fields):
    if not body:
        return fields[0] if fields else 'body'
    for field in fields:
        if field not in body:
            return field
    return None


def validate_float(value, min=None, max=None, name='field'):
    if value is None:
        raise ValidationError(f'{name} is required')
    try:
        v = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f'{name} must be a number')
    if min is not None and v < min:
        raise ValidationError(f'{name} must be at least {min}')
    if max is not None and v > max:
        raise ValidationError(f'{name} must be at most {max}')
    return v


def validate_int(value, min=None, max=None, name='field'):
    if value is None:
        raise ValidationError(f'{name} is required')
    try:
        v = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f'{name} must be an integer')
    if min is not None and v < min:
        raise ValidationError(f'{name} must be at least {min}')
    if max is not None and v > max:
        raise ValidationError(f'{name} must be at most {max}')
    return v


def validate_string(value, max_length=None, name='field'):
    if not isinstance(value, str):
        raise ValidationError(f'{name} must be a string')
    if max_length is not None and len(value) > max_length:
        raise ValidationError(f'{name} must be at most {max_length} characters')
    return value.strip()


_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def validate_email(value):
    v = validate_string(value, max_length=256, name='email')
    if not _EMAIL_RE.match(v):
        raise ValidationError('Invalid email format')
    return v.lower()


_UUID_RE = re.compile(r'^[0-9a-f]{64}$', re.IGNORECASE)


def validate_uuid(value):
    if not _UUID_RE.match(str(value)):
        raise ValidationError('Invalid UUID format')
    return str(value).lower()
