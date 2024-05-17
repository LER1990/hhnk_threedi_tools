# %%

import inspect
import logging
import sys
from logging import *  # noqa: F401,F403 # type: ignore
from pathlib import Path


def get_logger(name: str, level=logging.INFO, format_short=False):
    """
    Name should default to __name__, so the logger is linked to the correct file

    When using in a (sub)class, dont use this function. The logger will inherit the settings.
    Use:
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")


    Parameters
    ----------
    name : str
        Default use
        name = __name__
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    date_format = "%Y-%m-%d %H:%M:%S"

    # Log console entry format:
    # [<level> ][ <logger> ] <message>
    date_format_short = "%H:%M:%S"

    stdout_log_format = "[%(levelname)-8s][ %(name)s :%(lineno)s ] %(message)s"
    stdout_log_format = "[%(asctime)s][%(levelname)-8s][ %(name)s:%(lineno)s ] %(message)s"

    if format_short is True:
        stdout_log_format = "%(levelname)-5s | %(message)s"
    else:
        stdout_log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)-4s| %(message)s"

    stdout_log_formatter = logging.Formatter(stdout_log_format, date_format_short, style="%")

    # With this formatting we can search the code in vs-code. Use ctrl+P -> copy filename:lineno -> enter
    # e.g. ctrl+P -> logger.py:51 -> will get you to this file
    file_log_format = "[{asctime}][%(levelname)-8s][ %(filename)s:%(lineno)s ] %(message)s"
    file_log_formatter = logging.Formatter(file_log_format, date_format)

    # file_log_format = "[%(levelname)-8s]" "[ %(name)s :%(lineno)s ] " "%(message)s"
    # file_log_formatter = logging.Formatter(file_log_format)

    # def add_stdout_handler(loglevel: int = logging.INFO):
    #   handler = logging.StreamHandler()
    #   handler.setLevel(loglevel)
    #   handler.setFormatter(stdout_log_formatter)
    #   root.addHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(stdout_log_formatter)

    # print(handler)
    # print(logger.handlers)

    if len(logger.handlers) > 0:
        for handler in logger.handlers:
            # make sure no duplicate handlers are added
            if not isinstance(handler, logging.FileHandler) and not isinstance(handler, logging.StreamHandler):
                logger.addHandler(handler)
                logger.info("added logger hashandlers")
    else:
        logger.addHandler(handler)
        logger.info("added logger no handlers")

    return logger


# %%
import inspect
import sys
