from flask import Blueprint
from app.middlewares.validator_middleware import validate_fields
from app.services.record_service import RecordService

record_controller = Blueprint("record_controller", __name__)

@record_controller.route("/save-encounter", methods=["POST"])
@validate_fields([(["patient_id"])])
def save_record(valid_data):
    """API endpoint to upsert clinical encounter record."""
    return RecordService.save_record(valid_data)

@record_controller.route("/generate-soap", methods=["POST"])
def generate_soap():
    """API endpoint to upload a clinical encounter record."""
    return RecordService.generate_soap_notes()


@record_controller.route("/fetch-records", methods=["POST"])
@validate_fields([(["doctor_id"])])
def fetch_record(valid_data):
    """API endpoint to fetch clinical encounter record."""
    return RecordService.fetch_record(valid_data)


@record_controller.route("/get-record-by-id", methods=["POST"])
@validate_fields([(["record_id"])])
def get_record_by_id(valid_data):
    """API endpoint to fetch clinical encounter record by ID."""
    return RecordService.get_record_by_id(valid_data)