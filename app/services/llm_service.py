import json
from app.prompts.generate_soap_notes import GENERATE_SOAP_NOTES_PROMPT_SYSTEM, GENERATE_SOAP_NOTES_PROMPT_USER
from app.utils.openai_util import OpenAIUtil
import openai
from app.services.logging_service import global_logger
from app.utils.response_util import api_response


class LLMService:

    @staticmethod
    def generate_soap_notes(data):
        try:
            transcript = data.get("transcript")
            formatted_transcript = LLMService._format_transcript(transcript)
            soap_note = LLMService._generate_soap_note_with_openai(formatted_transcript)
            return api_response(
                status_code=200,
                message="SOAP notes generated successfully.",
                data={"soap_notes": soap_note},
            )

        except Exception as e:
            return LLMService._handle_exception(e, data)

    # ----------------- Internal Methods -----------------

    @staticmethod
    def _format_transcript(transcript):
        """Format transcript (string or list) for GPT prompt."""
        if isinstance(transcript, list):
            formatted = ""
            for entry in transcript:
                speaker = entry.get("speaker", "")
                text = entry.get("text", "")
                start_timestamp = entry.get("start_timestamp", "")
                end_timestamp = entry.get("end_timestamp", "")
                formatted += f"Speaker {speaker}, Timestamp: ({start_timestamp} - {end_timestamp}): {text}\n"
            return formatted
        return transcript  # assume string format already

    @staticmethod
    def _generate_soap_note_with_openai(transcript_text: str) -> str:
        try:
            # Initialize OpenAI utility with appropriate configuration
            openai_util = OpenAIUtil({
                "system_prompt": GENERATE_SOAP_NOTES_PROMPT_SYSTEM,
                "user_prompt": GENERATE_SOAP_NOTES_PROMPT_USER.format(transcript_text=transcript_text),
                "model": "gpt-4o",  # Specify a more capable model for medical content
                "temperature": 0.1,  # Low temperature for more consistent results
                "response_format": {"type": "json_object"}  # Proper format specification
            })
            
            # Call the API
            response = openai_util.get()
            
            # Parse the JSON response
            try:
                soap_note = json.loads(response)
            except json.JSONDecodeError:
                global_logger.log_event({
                    "message": "json_decode_error_soap_note",
                    "raw_response_length": len(response),
                    "raw_response_preview": response[:200] if response else None
                }, level="error")
                raise ValueError("Invalid JSON returned by OpenAI")
            
            # Validate required fields
            required_fields = ["subjective", "objective", "assessment", "plan"]
            missing_fields = [field for field in required_fields if field not in soap_note]
            
            if missing_fields:
                global_logger.log_event({
                    "message": "incomplete_soap_response",
                    "missing_fields": missing_fields,
                    "available_fields": list(soap_note.keys())
                }, level="warning")
                
                # Fill in missing fields with placeholders
                for field in missing_fields:
                    soap_note[field] = "Not provided in the transcript"
            
            return soap_note
            
        except Exception as e:
            # Log the error with limited transcript info to avoid PII exposure
            transcript_preview = transcript_text[:100] + "..." if transcript_text and len(transcript_text) > 100 else "[Empty transcript]"
            
            global_logger.log_event({
                "message": "error_generating_soap_note",
                "error": str(e),
                "transcript_preview": transcript_preview,
                "transcript_length": len(transcript_text) if transcript_text else 0
            }, level="error")
            
            raise Exception(f"Error generating SOAP note: {e}") from e

    @staticmethod
    def _handle_exception(error, request_data):
        global_logger.log_event(
            {
                "message": "error_generating_soap_notes",
                "error": str(error),
                "data": request_data,
            },
            level="error",
        )
        return api_response(
            status_code=500,
            message="Internal Server Error",
            data={"error": str(error)},
        )
