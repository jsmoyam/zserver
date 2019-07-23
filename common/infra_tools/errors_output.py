from flask import jsonify

from common.app_model import AppDataResultSchema, ErrorCode, AppDataResult


def create_output_on_error(error: ErrorCode) -> str:

    result = AppDataResult(success=False, status_code=error.code_http, error=error)
    response = jsonify(AppDataResultSchema().dumps(result))
    output = str(response.json[0])

    return output
