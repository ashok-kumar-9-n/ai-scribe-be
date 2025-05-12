import requests
from app.services.s3_service import S3Uploader
from flask import request
from app.utils.mongo_util import mongo_util
from app.utils.response_util import api_response
from app.services.logging_service import global_logger
from app.constants.constants import LOCAL_BASE_URL, RECORDS_COLLECTION
from bson import ObjectId

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
        
    @staticmethod
    def fetch_record(data):
        try:
            doctor_id = data.get("doctor_id")
            documents = mongo_util.find(
                RECORDS_COLLECTION,
                {"doctor_id": doctor_id},
                projection={
                    "_id": 1,
                    "patient_id": 1,
                    "doctor_id": 1,
                    "s3_url": 1
                }
            )

            if not documents:
                return api_response(
                    status_code=404,
                    message="No records found for this doctor_id.",
                    data={}
                )
            records = []
            for document in documents:
                document["_id"] = str(document["_id"])
                records.append(document)
            return api_response(
                status_code=200,
                message="Records fetched successfully.",
                data=records
            )
        except Exception as e:
            global_logger.log_event(
                {
                    "message": "error_fetching_clinical_record",
                    "error": str(e),
                    "data": data,
                },
                level="error"
            )
            return api_response(
                status_code=500,
                message="An error occurred while fetching the record.",
                data={"error": str(e)}
            )
        
    @staticmethod
    def get_record_by_id(data):
        try:
            record_id = data.get("record_id")
            document = mongo_util.find_one(
                RECORDS_COLLECTION,
                {"_id": ObjectId(record_id)}
            )
            if not document:
                return api_response(
                    status_code=404,
                    message="No records found for this record_id.",
                    data={}
                )
            document["_id"] = str(document["_id"])
            return api_response(
                status_code=200,
                message="Record fetched successfully.",
                data=document
            )
        except Exception as e:
            global_logger.log_event(
                {
                    "message": "error_fetching_clinical_record_by_id",
                    "error": str(e),
                    "data": data,
                },
                level="error"
            )
            return api_response(
                status_code=500,
                message="An error occurred while fetching the record.",
                data={"error": str(e)}
            )
        
    @staticmethod
    def _upload_to_s3():
        try:
            uploader = S3Uploader()
            s3_url = uploader.upload()
            return s3_url
        except Exception as e:
            global_logger.log_event(
                {
                    "message": "error_uploading_to_s3",
                    "error": str(e),
                },
                level="error"
            )
            return None
        
    @staticmethod
    def _get_transcript(media_url: str):
        try:
            response = requests.post(
                url=f'{LOCAL_BASE_URL}/api/deepgram/get-transcript',
                json={"media_url": media_url},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            json_data = response.json()
            return json_data.get("data").get("transcript", [])
        except requests.RequestException as e:
            global_logger.log_event(
                {
                    "message": "error_fetching_transcript",
                    "error": str(e),
                    "media_url": media_url,
                },
                level="error"
            )
            return []

    @staticmethod
    def _generate_soap_note_from_transcript(transcript):
        try:
            response = requests.post(
                url=f'{LOCAL_BASE_URL}/api/llm/generate-soap-notes',
                json={"transcript": transcript},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            json_data = response.json()
            return json_data.get("data").get("soap_notes", {})
        except requests.RequestException as e:
            global_logger.log_event(
                {
                    "message": "error_generating_soap_notes",
                    "error": str(e),
                },
                level="error"
            )
            return {}
        
    
    @staticmethod
    def _save_encounter_record_to_s3(data):
        try:
            result = mongo_util.insert_one(
                RECORDS_COLLECTION,
                data
            )
            if not result:
                raise Exception("Failed to save encounter record to MongoDB")
            
            return True
        except requests.RequestException as e:
            global_logger.log_event(
                {
                    "message": "error_saving_encounter_record",
                    "error": str(e),
                    "data": data,
                },
                level="error"
            )
            return False

    @staticmethod
    def generate_soap_notes():
        try:
            is_json = request.is_json
            patient_id = request.form.get('patient_id') or (request.json.get('patient_id') if is_json else None)
            doctor_id = request.form.get('doctor_id') or (request.json.get('doctor_id') if is_json else None)
            media_url = request.json.get('media_url') if is_json else None

            try:
                patient_id = int(patient_id)
                doctor_id = int(doctor_id)
            except (ValueError, TypeError):
                return api_response(400, message="Invalid patient_id or doctor_id")

            if not patient_id or not doctor_id or (is_json and not media_url):
                return api_response(400, message="Missing patient_id, doctor_id, or media")

            # if media_url exists then upload to s3 parallelly
            #     with concurrent.futures.ThreadPoolExecutor() as executor:
            #         s3_url_future = executor.submit(RecordService._upload_to_s3())
            #         transcript_future = executor.submit(RecordService._get_transcript, media_url)

            #         s3_url = s3_url_future.result()
            #         transcript = transcript_future.result()
            # else:
            s3_url = RecordService._upload_to_s3()
            transcript = RecordService._get_transcript(s3_url)
            soap_notes_data = RecordService._generate_soap_note_from_transcript(transcript)

            data_to_save = {
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "s3_url": s3_url,
                "transcript": transcript,
                "soap_notes": soap_notes_data,
            }

            # Save the encounter record to S3
            encounter_record = RecordService._save_encounter_record_to_s3(data_to_save)

            if not encounter_record:
                return api_response(500, message="Failed to save encounter record")
            
            if "_id" in data_to_save:
                data_to_save["_id"] = str(data_to_save["_id"])

            return api_response(200, message="SOAP notes generated successfully", data = data_to_save)
        except Exception as e:
            return api_response(500, message="Server Error: " + str(e))