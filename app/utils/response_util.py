import json
import datetime
import requests
import threading
from typing import Any
from flask import jsonify, request
from http import HTTPStatus
from app.services.logging_service import global_logger
from app.utils.general import extract_request_details

def api_response(status_code: int, message: str = None, data: Any = None):
    """
        Returns a JSON response with the status code, message and data

        Args:
            status_code: The status code of the response
            message: The message to be included in the response
            data: The data to be included in the response

        Returns:
            A JSON response with the status code
    """
    status_phrase = HTTPStatus(status_code).phrase

    response = {
        "status": status_phrase,
        "status_code": status_code,
        "message": message,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if data:
        response["data"] = data

    return jsonify(response), status_code