import io
from PIL import Image

from app.minio_client import MinioClient
from app.pika_queue import ReceiveQueue, SendQueue

BUCKET_SRC = "to-process"
BUCKET_DEST = "processed"


class Worker:
    def __init__(self):
        self.client = MinioClient()
        self.request_queue = ReceiveQueue(BUCKET_SRC)
        self.response_queue = SendQueue(BUCKET_DEST)

    def process_queue(self):
        def on_message(filename: str):
            file_data = self.client.get_file(BUCKET_SRC, filename)
            file = io.BytesIO(file_data)
            output = self.convert_image(file)

            size = output.getbuffer().nbytes
            self.client.upload_file(BUCKET_DEST, filename, output, size, "image/png")
            self.response_queue.add_to_queue(f"Processed {filename}")

        self.request_queue.receive_message(on_message)

    def convert_image(self, file: io.BytesIO) -> io.BytesIO:
        image = Image.open(file)

        image_grayscale = image.convert("L")
        output = io.BytesIO()
        image_grayscale.save(output, format="PNG")
        output.seek(0)
        return output


if __name__ == "__main__":
    worker = Worker()
    worker.process_queue()
