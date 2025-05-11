from app.services.logging_service import global_logger
from app.utils.response_util import api_response

class LLMService:

    @staticmethod
    def generate_soap_notes(data):
        try:
            transcript = data.get("transcript")
            return LLMService._build_response(transcript)

        except Exception as e:
            return LLMService._handle_exception(e, data)

    # ----------------- Internal Methods -----------------

    @staticmethod
    def _build_response(transcript):
        return api_response(
            status_code=200,
            message="SOAP notes generated successfully.",
            data={"soap_notes": transcript},
        )

    @staticmethod
    def _handle_exception(error, request_data):
        global_logger.log_event(
            {
                "message": "error_generating_soap_notes",
                "error": str(error),
                "data": request_data
            },
            level="error"
        )
        return api_response(
            status_code=500,
            message="Internal Server Error",
            data={"error": str(error)}
        )
