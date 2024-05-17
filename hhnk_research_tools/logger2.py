# %%
import logging
from logging import *  # noqa: F401,F403 # type: ignore
from pathlib import Path

root = logging.getLogger()
root.setLevel(logging.DEBUG)

date_format = "%Y-%m-%d %H:%M:%S"

# Log console entry format:
# [<level> ][ <logger> ] <message>
stdout_log_format = "[%(levelname)-8s]" "[ %(name)s ] " "%(message)s"
stdout_log_formatter = logging.Formatter(stdout_log_format)


def add_stdout_handler(loglevel: int = logging.INFO):
    handler = logging.StreamHandler()
    handler.setLevel(loglevel)
    handler.setFormatter(stdout_log_formatter)

    if len(root.handlers) > 0:
        for handler in root.handlers:
            # make sure no duplicate handlers are added
            if not isinstance(handler, logging.FileHandler) and not isinstance(handler, logging.StreamHandler):
                root.addHandler(handler)
                root.info("added logger1")
    else:
        root.addHandler(handler)
        root.info("added logger2")


def file_log_filter(record):
    if record.name == "root":
        record.qualifiedFuncName = "." + record.funcName
    else:
        record.qualifiedFuncName = record.name + "." + record.funcName
    return True


# Log file entry format:
# [<time>][<level> ][ <file>:<line> ][ <class>.<function>() ] <message>
file_log_format = (
    "[%(asctime)s]" "[%(levelname)-8s]" "[ %(filename)s:%(lineno)s ]" "[ %(qualifiedFuncName)s() ] " "%(message)s"
)
file_log_formatter = logging.Formatter(file_log_format, date_format)


def add_file_handler(logfile: Path, loglevel: int = logging.DEBUG):
    logfile.parent.mkdir(parents=True, exist_ok=True)
    logfile.unlink(missing_ok=True)
    handler = logging.FileHandler(str(logfile))
    handler.setLevel(loglevel)
    handler.addFilter(file_log_filter)
    handler.setFormatter(file_log_formatter)
    root.addHandler(handler)
