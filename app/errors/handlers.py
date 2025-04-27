from flask import request, jsonify, Response
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException, InternalServerError

from .base_error import BaseError
from .validation_error import PydanticValidationError


def handle_custom_error(e: BaseError) -> tuple[Response, int]:
    base = e.to_dict()
    base["service"] = request.blueprint or "main"
    return jsonify(base), e.status


def handle_validation_error(e: ValidationError) -> tuple[Response, int]:
    return handle_custom_error(PydanticValidationError(e))


def handle_http_exception(e: HTTPException) -> tuple[Response, int]:
    response = {
        "error": e.name,
        "code": e.code,
        "description": e.description
    }
    return jsonify(response), e.code


def handle_unexpected_error(_: Exception) -> tuple[Response, int]:
    return handle_http_exception(InternalServerError())
