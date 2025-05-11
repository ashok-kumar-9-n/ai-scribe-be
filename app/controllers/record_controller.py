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


@record_controller.route("/fetch-record", methods=["POST"])
@validate_fields([(["doctor_id"])])
def fetch_record(valid_data):
    """API endpoint to fetch clinical encounter record."""
    return RecordService.fetch_record(valid_data)