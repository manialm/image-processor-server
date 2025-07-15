import logging


def get_logger(name: str):

    class Filter(logging.Filter):
        def filter(self, record):
            return record.name == name

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.addFilter(Filter())
    # logger.handlers.clear()
    formatter = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
