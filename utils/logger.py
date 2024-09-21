import logging


class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def debug(self, message: str):
        self.logger.debug(message)


if __name__ == "__main__":
    logger = Logger("test")
    logger.info("This is an info message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.debug("This is a debug message")
