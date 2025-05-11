import json
import requests
from app.constants.config import DEEPGRAM_API_KEY
from app.constants.constants import DEEPGRAM_BASE_URL
from app.utils.response_util import api_response
from app.services.logging_service import global_logger

class DeepgramService:

    @staticmethod
    def get_transcript(data):
        media_url = data.get("media_url")
        try:
            response = DeepgramService._fetch_from_deepgram(media_url)
            if response.status_code != 200:
                return DeepgramService._handle_api_error(response, data)

            paragraphs = DeepgramService._extract_paragraphs(response.json())
            transcript = DeepgramService._merge_consecutive_speaker_sentences(paragraphs)

            return api_response(
                status_code=200,
                message="Transcript fetched successfully.",
                data={"transcript": transcript, "media_url": media_url},
            )

        except Exception as e:
            return DeepgramService._handle_exception(e, data)

    # ----------------- Internal Methods -----------------

    @staticmethod
    def _fetch_from_deepgram(media_url):
        url = f"{DEEPGRAM_BASE_URL}/v1/listen?model=nova-3-medical&smart_format=true&diarize=true"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = json.dumps({"url": media_url})
        return requests.post(url, headers=headers, data=payload)

    @staticmethod
    def _extract_paragraphs(response_json):
        return (
            response_json
            .get("results", {})
            .get("channels", [{}])[0]
            .get("alternatives", [{}])[0]
            .get("paragraphs", {})
            .get("paragraphs", [])
        )

    @staticmethod
    def _merge_consecutive_speaker_sentences(paragraphs):
        merged = []
        current_block = None

        for segment in paragraphs:
            speaker = segment.get("speaker")
            for sentence in segment.get("sentences", []):
                try:
                    start = sentence.get("start")
                    end = sentence.get("end")
                    text = sentence.get("text", "").strip()
                    if start is None or end is None or not text:
                        continue

                    if current_block and current_block["speaker"] == speaker:
                        current_block["end_timestamp"] = end
                        current_block["text"] += " " + text
                    else:
                        if current_block:
                            merged.append(current_block)
                        current_block = {
                            "speaker": speaker,
                            "start_timestamp": start,
                            "end_timestamp": end,
                            "text": text,
                        }
                except Exception as e:
                    print(f"Skipped malformed sentence: {sentence} due to error: {e}")

        if current_block:
            merged.append(current_block)

        return merged

    @staticmethod
    def _handle_api_error(response, request_data):
        global_logger.log_event(
            {
                "message": "error_fetching_deepgram_transcript",
                "data": request_data,
                "response": response.json(),
            },
            level="error",
        )
        return api_response(
            status_code=response.status_code,
            message="Failed to fetch transcript.",
            data=response.json(),
        )

    @staticmethod
    def _handle_exception(error, request_data):
        global_logger.log_event(
            {
                "message": "exception_during_transcript_fetch",
                "error": str(error),
                "data": request_data,
            },
            level="error",
        )
        return api_response(
            status_code=500,
            message="An error occurred while fetching the transcript.",
            data={"error": str(error)},
        )