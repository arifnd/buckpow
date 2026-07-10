class AppError(Exception):
    def __init__(self, message, status_code=400, code=None):
        self.message = message
        self.status_code = status_code
        self.code = code


class ValidationError(AppError):
    def __init__(self, message, code='VALIDATION_ERROR'):
        super().__init__(message, 400, code)


class NotFoundError(AppError):
    def __init__(self, message='Resource not found', code='NOT_FOUND'):
        super().__init__(message, 404, code)


class AuthError(AppError):
    def __init__(self, message, code='AUTH_ERROR'):
        super().__init__(message, 401, code)
