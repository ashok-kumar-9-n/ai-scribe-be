import json
from datetime import datetime
from app.prompts.generate_soap_notes import SOAP_NOTES_SYSTEM_PROMPT, SOAP_NOTES_USER_PROMPT
from app.utils.openai_util import OpenAIUtil
from typing import Dict, Any
from app.services.logging_service import global_logger
from app.utils.response_util import api_response


class LLMService:
    @staticmethod
    def generate_soap_notes(data):
        try:
            transcript = data.get("transcript")
            formatted_transcript = LLMService._format_transcript(transcript)
            soap_note = LLMService.generate_soap_note_from_transcript(formatted_transcript)
            return api_response(
                status_code=200,
                message="SOAP notes generated successfully.",
                data={"soap_notes": soap_note, "report_generation_time": datetime.now().isoformat()},
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
    def generate_soap_note_from_transcript(transcript_text: str) -> Dict[str, Any]:
        """
        Generate a structured SOAP note from a medical transcript using OpenAI.
        
        Args:
            transcript_text: The transcript of the doctor-patient conversation.
            
        Returns:
            Dictionary containing the structured SOAP note with keys for 
            subjective, objective, assessment, plan, and evidence mapping.
            
        Raises:
            Exception: If there is an error generating or parsing the SOAP note.
        """
       
        try:
            # Initialize OpenAI utility with appropriate configuration
            openai_util = OpenAIUtil({
                "system_prompt": SOAP_NOTES_SYSTEM_PROMPT,
                "user_prompt": SOAP_NOTES_USER_PROMPT.format(transcript_text=transcript_text),
                "response_format": {"type": "json_object"}
            })
            
            # Call the API
            response = openai_util.get()
            # Parse the result
            if isinstance(response, str):
                return json.loads(response)
            elif isinstance(response, dict):
                return response
            else:
                raise ValueError("Unexpected response format from OpenAI.")
            
        except Exception as e:
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