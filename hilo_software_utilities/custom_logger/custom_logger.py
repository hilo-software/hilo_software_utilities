import os
import logging
from logging.handlers import TimedRotatingFileHandler

CUSTOM_LEVEL_NUM = 25
CUSTOM_LEVEL_NAME = "CUSTOM"
DEFAULT_LOGGING_LEVEL = CUSTOM_LEVEL_NUM

def setup_logging_handlers(log_file: str, rotate: bool, backup_count: int) -> list:
    try:
        if not rotate:
            # Remove existing log file to start fresh
            if os.path.exists(log_file):
                os.remove(log_file)
            
            # Create a basic file handler in write mode
            logging_file_handler = logging.FileHandler(log_file, mode='w')

        else:
            # Timed rotation (e.g., daily), keep specified backups
            logging_file_handler = TimedRotatingFileHandler(
                log_file, when='D', interval=1, backupCount=backup_count
            )
            # Do NOT force rollover — let it happen naturally based on time

    except (IOError, OSError, ValueError, FileNotFoundError) as e:
        print(f'ERROR -- Could not create logging file: {log_file}, e: {str(e)}')
        return [logging.StreamHandler()]
    except Exception as e:
        print(f'ERROR -- Unexpected Exception: Could not create logging file: {log_file}, e: {str(e)}')
        return [logging.StreamHandler()]

    return [logging_file_handler, logging.StreamHandler()]

# Define formats
default_format = "%(asctime)s %(levelname)s: %(message)s"
info_format = "%(message)s"
custom_format = "%(asctime)s CUSTOM: %(message)s"


def custom(self, message, *args, **kws):
    if self.isEnabledFor(CUSTOM_LEVEL_NUM):
        self._log(CUSTOM_LEVEL_NUM, message, args, **kws)


class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, info_fmt=None, custom_fmt=None, *args, **kwargs):
        super().__init__(fmt, datefmt, *args, **kwargs)
        self.default_fmt = fmt
        self.info_fmt = info_fmt
        self.custom_fmt = custom_fmt

    def format(self, record):
        # Use different format for INFO level
        if record.levelno == logging.INFO:
            self._style._fmt = self.info_fmt # type: ignore
        # Use different format for CUSTOM level
        elif record.levelno == CUSTOM_LEVEL_NUM:
            self._style._fmt = self.custom_fmt # type: ignore
            record.levelname = CUSTOM_LEVEL_NAME  # Ensure the custom level name is used
        else:
            self._style._fmt = self.default_fmt # type: ignore
        return super().format(record)


def init_logging(log_file: str, level=DEFAULT_LOGGING_LEVEL, rotate: bool=False, backup_count: int=0) -> logging.Logger:
    logging.addLevelName(CUSTOM_LEVEL_NUM, CUSTOM_LEVEL_NAME)
    logging.Logger.custom = custom  # type: ignore
    logger = logging.getLogger('')
    logger.setLevel(level)
    formatter = CustomFormatter(fmt=default_format, info_fmt=info_format, custom_fmt=custom_format, datefmt="%Y-%m-%d %H:%M:%S")
    logging_handlers = setup_logging_handlers(log_file, rotate, backup_count)
    for handler in logging_handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
