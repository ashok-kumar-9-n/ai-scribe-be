from flask import Blueprint
from app.middlewares.validator_middleware import validate_fields
from app.services.deepgram_service import DeepgramService

deepgram_controller = Blueprint("deepgram_controller", __name__)

@deepgram_controller.route("/get-transcript", methods=["POST"])
@validate_fields([(["media_url"])])
def get_transcript(valid_data):
    """API endpoint to get transcript from Deepgram."""
    return DeepgramService.get_transcript(valid_data)
