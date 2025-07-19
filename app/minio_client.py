from datetime import timedelta
from typing import Annotated, BinaryIO
from functools import lru_cache

from fastapi import Depends
from minio import Minio
from minio.error import S3Error
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.settings import settings

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


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
            logger.debug(f"Bucket '{bucket_name}' created.")
        else:
            logger.debug(f"Bucket '{bucket_name}' already exists.")

        result = self.client.put_object(
            bucket_name, filename, file_data, file_size, content_type
        )

        logger.debug(
            f"'{result.object_name}' successfully uploaded to bucket '{result.bucket_name}'."
        )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15)
    )
    def upload_file(
        self,
        bucket_name: str,
        filename: str,
        file_data: BinaryIO,
        file_size: int,
        content_type: str,
    ):
        try:
            logger.debug(
                f"Attempting to upload file {filename} to bucket {bucket_name}"
            )
            self.try_upload_file(
                bucket_name, filename, file_data, file_size, content_type
            )
        except S3Error as exc:
            logger.error(f"Error occurred during upload: {exc}")
            raise

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15)
    )
    def get_file_url(self, bucket_name: str, filename: str):
        try:
            logger.debug(f"Attempting to get file url for {filename}")
            url = self.client.presigned_get_object(
                bucket_name, filename, timedelta(minutes=30)
            )

            return url

        except Exception as exc:
            logger.error(f"Error occurred during get file: {exc}")
            raise

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15)
    )
    def get_file(self, bucket_name: str, filename: str):
        response = None
        try:
            response = self.client.get_object(bucket_name, filename)

            content = response.read()
            # content_type = response.headers.get(
            #     "Content-Type", "application/octet-stream"
            # )
            return content

        finally:
            if response:
                response.close()
                response.release_conn()


@lru_cache()
def get_minio_client():
    return MinioClient()


MinioClientDep = Annotated[MinioClient, Depends(get_minio_client)]
