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
    if status_code >= 500:
        request_info = extract_request_details(request)
        thread = threading.Thread(target=send_error_alert_to_slack, args=(status_code, message, request_info, data))
        thread.start()

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

def send_error_alert_to_slack(status_code, error_message, request_info, data):
    
    url = request_info.get("request_url")

    request_info.pop('headers', None)
    request_info_str = "\n".join([f"{key.upper()}: {value}" for key, value in request_info.items()])
    global_logger.log_event(
        {
            "message": "Error Alert",
            "status_code": status_code,
            "error_message": error_message,
            "request_info": request_info_str,
            "data": data,
            "url": url,
            "method": request_info.get("method"),
            "body": request_info.get("body"),
            "remote_addr": request_info.get("remote_addr"),
        },
        level="error"
    )
