from datetime import datetime
import sys

import logging
import logging.handlers

from rich.logging import RichHandler

MANUAL = False

def set_logger(LOG_PATH, RICH_FORMAT, FILE_HANDLER_FORMAT) -> logging.Logger:
    logging.basicConfig(
        level="NOTSET",
        format=RICH_FORMAT,
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    #add now_time to LOG_PATH (for example, BasicCrawer_2024-05-15.log)
    LOG_PATH = LOG_PATH.split(".log")
    LOG_PATH = LOG_PATH[0] + "_" + str(datetime.now().date()) + ".log"
    logger = logging.getLogger("rich")

    file_handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(FILE_HANDLER_FORMAT))
    logger.addHandler(file_handler)

    return logger

def handle_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger("rich")

    logger.error("Unexpected exception",
                 exc_info=(exc_type, exc_value, exc_traceback))