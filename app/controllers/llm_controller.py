from flask import Blueprint
from app.services.llm_service import LLMService
from app.middlewares.validator_middleware import validate_fields

llm_controller = Blueprint("llm_controller", __name__)

@llm_controller.route("/generate-soap-notes", methods=["POST"])
@validate_fields([(["transcript"])])
def generate_soap_notes(valid_data):
    return LLMService.generate_soap_notes(valid_data)
