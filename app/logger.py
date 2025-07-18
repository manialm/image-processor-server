import logging
import sys


def get_logger(name: str):

    class Filter(logging.Filter):
        def filter(self, record):
            return record.name == name

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(Filter())

    file_handler = logging.FileHandler("info.log")
    formatter = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
    file_handler.setFormatter(formatter)

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(file_handler)

    return logger
