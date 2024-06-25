from rest_framework import exceptions


class CustomValidationError(exceptions.APIException):
    """
    Custom exception class validation errors
    """
    status_code = 400
    default_detail = {}

    def __init__(self, detail=None):
        if detail is None:
            detail = self.default_detail
        super().__init__(detail=detail)
