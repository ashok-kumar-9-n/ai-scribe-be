from flask import request
from app.utils.mongo_util import mongo_util
from app.utils.response_util import api_response
from app.services.logging_service import global_logger
from app.constants.constants import RECORDS_COLLECTION

class RecordService:

    @staticmethod
    def save_record(data):
        try:
            patient_id = data.get("patient_id")

            json_request = request.json
            if "patient_id" in json_request:
                del json_request["patient_id"]
                
            result = mongo_util.update_one(
                RECORDS_COLLECTION,
                {"patient_id": patient_id},
                {
                    "$set": json_request,
                },
                upsert=True,
            )

            return api_response(
                status_code=200,
                message="Record upserted successfully.",
                data={
                    "patient_id": patient_id,
                    "matched": result.matched_count,
                    "modified": result.modified_count,
                    "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                    "record": json_request,
                }
            )
        except Exception as e:
            global_logger.log_event(
                {
                    "message": "error_upserting_clinical_record",
                    "error": str(e),
                    "data": data,
                },
                level="error"
            )
            return api_response(
                status_code=500,
                message="An error occurred while saving the record.",
                data={"error": str(e)}
            )
