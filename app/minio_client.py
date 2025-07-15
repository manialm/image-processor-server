from typing import BinaryIO
import logging

from minio import Minio
from minio.error import S3Error

from app.core.settings import settings

from app.logger import get_logger

logger = get_logger(__name__)


class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_HOST,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
        )

    def try_upload_file(
        self,
        bucket_name: str,
        filename: str,
        file_data: BinaryIO,
        file_size: int,
        content_type: str,
    ):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
            logger.info(f"Bucket {bucket_name} created.")
        else:
            logger.info(f"Bucket {bucket_name} already exists.")

        result = self.client.put_object(
            bucket_name, filename, file_data, file_size, content_type
        )

        # check for success
        if result.object_name:
            logger.info(
                f"{result.object_name} successfully uploaded to bucket {result.bucket_name}."
            )
        else:
            logger.error(f"Error occurred during upload: {result.etag}")

    def upload_file(
        self,
        bucket_name: str,
        filename: str,
        file_data: BinaryIO,
        file_size: int,
        content_type: str,
    ):
        try:
            self.try_upload_file(
                bucket_name, filename, file_data, file_size, content_type
            )
        except S3Error as exc:
            logger.error(f"Error occurred during upload: {exc}")
