import os
import uuid
import mimetypes
import requests
from flask import request
from app.utils.s3_client import get_s3_client
from app.constants.config import AWS_S3_BUCKET_NAME, AWS_REGION_NAME

class S3Uploader:
    def __init__(self):
        self.s3_client = get_s3_client()
        self.bucket_name = AWS_S3_BUCKET_NAME
        self.region = AWS_REGION_NAME

    def upload(self):
        if 'file' in request.files:
            return self._upload_file(request.files['file'])

        if request.is_json and 'media_url' in request.json:
            return self._upload_from_url(request.json['media_url'])

        raise ValueError("No file or media_url provided")

    def _upload_file(self, file_obj):
        filename = self._generate_file_name(file_obj.filename)
        self._s3_upload(file_obj, filename)
        return self._build_url(filename)

    def _upload_from_url(self, media_url):
        try:
            with requests.get(media_url, stream=True, timeout=5) as response:
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "")
                filename = self._generate_file_name(media_url, content_type)
                self._s3_upload(response.raw, filename)
                return self._build_url(filename)
        except requests.RequestException as e:
            raise ValueError(f"Media download failed: {str(e)}")

    def _generate_file_name(self, source_name, content_type=None):
        ext = os.path.splitext(source_name.split("?")[0])[1]
        if not ext and content_type:
            ext = mimetypes.guess_extension(content_type) or ''
        return f"{uuid.uuid4()}{ext}"

    def _s3_upload(self, file_stream, filename):
        self.s3_client.upload_fileobj(
            Fileobj=file_stream,
            Bucket=self.bucket_name,
            Key=filename
        )

    def _build_url(self, filename):
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
