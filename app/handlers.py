import traceback

from flask import request, jsonify, Response as FlaskResponse
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException, InternalServerError
from flask_pydantic_spec import Request, Response as SpecResponse, FlaskPydanticSpec

from app.errors import ValidationFailed


def handle_http_exception(e: HTTPException) -> tuple[FlaskResponse, int]:
    response = {
        "error": e.name,
        "code": e.code,
        "description": e.description
    }
    return jsonify(response), e.code


def handle_validation_error(e: ValidationError) -> tuple[FlaskResponse, int]:
    simplified_errors = [
        {
            "parameter": err["loc"][0],
            "message": err["msg"],
            "value": err["input"]
        }
        for err in e.errors()
    ]
    return handle_http_exception(ValidationFailed(simplified_errors))


def handle_unexpected_error(e: Exception) -> tuple[FlaskResponse, int]:
    service_name = request.blueprint or "APP"
    tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
    print(f"[{service_name}] Unexpected error:\n{tb_str}")
    return handle_http_exception(InternalServerError())


def handle_spec_422(_req: Request, resp: SpecResponse, resp_validation_error: ValidationError,
                    _instance: FlaskPydanticSpec) -> SpecResponse:
    if resp_validation_error:
        raise resp_validation_error
    return resp
