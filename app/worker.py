import io
import logging
from PIL import Image

from app.minio_client import MinioClient
from app.pika_queue import ReceiveQueue, SendQueue
from app.core.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG) 


class Worker:
    def __init__(self):
        self.client = MinioClient()
        self.request_queue = ReceiveQueue(settings.BUCKET_TO_PROCESS)
        self.response_queue = SendQueue(settings.BUCKET_PROCESSED)

    def process_queue(self):
        def on_message(filename: str):
            file_data = self.client.get_file(settings.BUCKET_TO_PROCESS, filename)
            file = io.BytesIO(file_data)

            logger.debug(f"Converting image {filename} to grayscale")
            output = self.convert_image_to_grayscale(file)
            logger.debug(f"Finished converting image {filename} to grayscale")

            size = output.getbuffer().nbytes
            self.client.upload_file(
                settings.BUCKET_PROCESSED, filename, output, size, "image/png"
            )
            self.response_queue.add_to_queue(f"Processed {filename}")

        self.request_queue.receive_messages(on_message)

    def convert_image_to_grayscale(self, file: io.BytesIO) -> io.BytesIO:
        image = Image.open(file)

        image_grayscale = image.convert("L")
        output = io.BytesIO()
        image_grayscale.save(output, format="PNG")
        output.seek(0)

        return output

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.request_queue.close()
        self.response_queue.close()


if __name__ == "__main__":
    with Worker() as worker:
        worker = Worker()
        worker.process_queue()
