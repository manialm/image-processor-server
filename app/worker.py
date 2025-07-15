import io
from PIL import Image

from app.minio_client import MinioClient
from app.pika_queue import ReceiveQueue

BUCKET_SRC = "to-process"
BUCKET_DEST = "processed"


class Worker:
    def __init__(self):
        self.client = MinioClient()
        self.queue = ReceiveQueue(BUCKET_SRC)

    def process_queue(self):
        def on_message(filename: str):
            file_data, content_type = self.client.get_file(BUCKET_SRC, filename)
            file = io.BytesIO(file_data)
            output = self.convert_image(file)

            size = output.getbuffer().nbytes
            self.client.upload_file(BUCKET_DEST, filename, output, size, "image/png")

        self.queue.receive_message(on_message)

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
