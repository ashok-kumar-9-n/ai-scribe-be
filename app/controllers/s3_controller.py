from flask import Blueprint
from app.services.s3_service import S3Uploader
from app.utils.response_util import api_response

s3_controller = Blueprint("s3_controller", __name__)


@s3_controller.route("/upload", methods=["POST"])
def upload_to_s3():
    try:
        uploader = S3Uploader()
        s3_url = uploader.upload()
        return api_response(200, data={"s3_url": s3_url}, message="Video uploaded successfully")
    except ValueError as ve:
        return api_response(400, message=str(ve))
    except Exception as e:
        return api_response(500, message="Server Error: " + str(e))
