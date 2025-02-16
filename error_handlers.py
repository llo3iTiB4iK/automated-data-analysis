from werkzeug.exceptions import MethodNotAllowed
import os


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
    }, 405


def file_not_found(error: FileNotFoundError) -> tuple:
    return {
        "error": "dataset_not_found",
        "error_description": f"Dataset with ID '{os.path.basename(error.filename)}' not found in storage."
    }, 404
