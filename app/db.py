import sqlite3

from app.core.settings import settings
from app.pika_queue import ReceiveQueue


class DB:
    def __init__(self):
        self.conn = sqlite3.connect("messages.db")
        self.create_table()

    def create_table(self):
        with self.conn as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS messages(message TEXT)")

    def write_queue_messages_to_db(self):
        self.response_queue = ReceiveQueue(settings.BUCKET_PROCESSED)

        def on_message(message: str):
            self.add_message_to_db(message)

        self.response_queue.receive_messages(on_message)

    def add_message_to_db(self, message: str):
        with self.conn as conn:
            conn.execute("INSERT INTO messages VALUES (?)", [message])

    def get_messages(self):
        with self.conn as conn:
            result = conn.execute("SELECT message from messages")
            return result.fetchall()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        if getattr(self, "response_queue", None):
            self.response_queue.close()


if __name__ == "__main__":
    with DB() as db:
        db.write_queue_messages_to_db()
