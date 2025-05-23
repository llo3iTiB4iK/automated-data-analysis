import traceback

from flask import request, jsonify, Response
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException, InternalServerError

from app.errors import ValidationFailed


def handle_http_exception(e: HTTPException) -> tuple[Response, int]:
    response = {
        "error": e.name,
        "code": e.code,
        "description": e.description
    }
    return jsonify(response), e.code


def handle_validation_error(e: ValidationError) -> tuple[Response, int]:
    simplified_errors = [
        {
            "parameter": err["loc"][0],
            "message": err["msg"],
            "value": err["input"]
        }
        for err in e.errors()
    ]
    return handle_http_exception(ValidationFailed(simplified_errors))


def handle_unexpected_error(e: Exception) -> tuple[Response, int]:
    service_name = request.blueprint or "main"
    tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
    print(f"[{service_name}] Unexpected error:\n{tb_str}")
    return handle_http_exception(InternalServerError())
