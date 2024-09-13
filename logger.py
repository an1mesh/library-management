import logging

class CustomLogger:
    def __init__(self, name='my_logger', log_file='app.log', log_level=logging.DEBUG):
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        self.file_handler = logging.FileHandler(log_file,mode='w')
        self.file_handler.setLevel(log_level)

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        self.stream_handler.setFormatter(formatter)

        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stream_handler)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
