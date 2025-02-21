from flask import url_for
from werkzeug.exceptions import MethodNotAllowed, RequestEntityTooLarge
import errno


def missing_parameter(error: KeyError) -> tuple:
    return {
        "error": "bad_request",
        "error_description": f"Parameter '{error.args[0]}' is missing in the request"
    }, 400


def incorrect_parameter(error: ValueError) -> tuple:
    return {
        "error": "invalid_value",
        "error_description": error.args[0]
    }, 400


def method_not_allowed(error: MethodNotAllowed) -> tuple:
    return {
        "error": "method_not_allowed",
        "error_description": f"This endpoint only supports the following HTTP methods: {error.valid_methods}"
    }, error.code


def file_too_large(error: RequestEntityTooLarge) -> tuple:
    return {
        "error": "file_too_large",
        "error_description": "The uploaded file exceeds the maximum allowed size."
    }, error.code


def failed_to_store(error: OSError) -> tuple:
    if error.errno == errno.ENOSPC:
        return {
            "error": "storage_full",
            "error_description": f"Insufficient storage space. Unable to store the dataset. Try again later.\n"
                                 f"Alternatively, you can consider using {url_for('analyze_data')} endpoint."
        }, 507
    else:
        return {
            "error": "storage_error",
            "error_description": "An unexpected storage error occurred. Check your request or try again later."
        }, 500
