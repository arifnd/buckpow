import pytest
from src.utils.errors import (AppError, ValidationError, NotFoundError,
                               AuthError)
from src.utils.hash import hash_password, verify_password
from src.utils.validators import (validate_required, validate_float,
                                   validate_int, validate_string,
                                   validate_email, validate_uuid)


class TestAppError:
    def test_app_error_defaults(self):
        e = AppError('Something went wrong')
        assert e.message == 'Something went wrong'
        assert e.status_code == 400
        assert e.code is None

    def test_app_error_custom(self):
        e = AppError('Custom error', status_code=418, code='TEAPOT')
        assert e.status_code == 418
        assert e.code == 'TEAPOT'

    def test_validation_error(self):
        e = ValidationError('Invalid input')
        assert e.status_code == 400
        assert e.code == 'VALIDATION_ERROR'

    def test_not_found_error(self):
        e = NotFoundError()
        assert e.status_code == 404
        assert e.code == 'NOT_FOUND'
        assert e.message == 'Resource not found'

    def test_not_found_error_custom(self):
        e = NotFoundError('Device not found')
        assert e.message == 'Device not found'

    def test_auth_error(self):
        e = AuthError('Unauthorized')
        assert e.status_code == 401
        assert e.code == 'AUTH_ERROR'


class TestValidators:
    def test_validate_required_present(self):
        result = validate_required({'name': 'test', 'age': 25}, ['name', 'age'])
        assert result is None

    def test_validate_required_missing(self):
        result = validate_required({'name': 'test'}, ['name', 'age'])
        assert result == 'age'

    def test_validate_required_none_body(self):
        result = validate_required(None, ['field'])
        assert result == 'field'

    def test_validate_required_empty_fields(self):
        result = validate_required({}, [])
        assert result == 'body'

    def test_validate_float_valid(self):
        assert validate_float('3.14') == 3.14
        assert validate_float(42) == 42.0

    def test_validate_float_none(self):
        with pytest.raises(ValidationError, match='required'):
            validate_float(None)

    def test_validate_float_invalid(self):
        with pytest.raises(ValidationError, match='must be a number'):
            validate_float('abc')

    def test_validate_float_min(self):
        with pytest.raises(ValidationError, match='at least'):
            validate_float(5, min=10)

    def test_validate_float_max(self):
        with pytest.raises(ValidationError, match='at most'):
            validate_float(20, max=10)

    def test_validate_int_valid(self):
        assert validate_int('42') == 42

    def test_validate_int_none(self):
        with pytest.raises(ValidationError, match='required'):
            validate_int(None)

    def test_validate_int_invalid(self):
        with pytest.raises(ValidationError, match='must be an integer'):
            validate_int('not_an_int')

    def test_validate_int_min(self):
        with pytest.raises(ValidationError, match='at least'):
            validate_int(3, min=5)

    def test_validate_int_max(self):
        with pytest.raises(ValidationError, match='at most'):
            validate_int(10, max=5)

    def test_validate_string_valid(self):
        assert validate_string('hello') == 'hello'

    def test_validate_string_not_string(self):
        with pytest.raises(ValidationError, match='must be a string'):
            validate_string(123)

    def test_validate_string_max_length(self):
        with pytest.raises(ValidationError, match='at most'):
            validate_string('too long', max_length=3)

    def test_validate_string_strips(self):
        assert validate_string('  spaced  ') == 'spaced'

    def test_validate_email_valid(self):
        assert validate_email('Test@Example.com') == 'test@example.com'

    def test_validate_email_no_at(self):
        with pytest.raises(ValidationError, match='Invalid email'):
            validate_email('notanemail')

    def test_validate_email_no_domain(self):
        with pytest.raises(ValidationError, match='Invalid email'):
            validate_email('user@')

    def test_validate_email_invalid_type(self):
        with pytest.raises(ValidationError, match='must be a string'):
            validate_email(123)

    def test_validate_uuid_valid(self):
        uuid_hex = 'a' * 64
        assert validate_uuid(uuid_hex) == uuid_hex

    def test_validate_uuid_invalid(self):
        with pytest.raises(ValidationError, match='Invalid UUID'):
            validate_uuid('short')

    def test_validate_uuid_wrong_chars(self):
        with pytest.raises(ValidationError, match='Invalid UUID'):
            validate_uuid('z' + '0' * 63)


class TestHash:
    def test_verify_password_corrupt_hash(self):
        assert verify_password('anything', 'not-a-bcrypt-hash') is False
