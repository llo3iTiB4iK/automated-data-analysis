def missing_parameter(error):
    return {
        "error": "bad_request",
        "error_description": f"Parameter '{error.args[0]}' is missing in the request"
    }, 400


def incorrect_parameter(error: ValueError):
    return {
        "error": "invalid_value",
        "error_description": error.args[0]
    }, 400
