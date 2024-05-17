# %%

import test_logger

import hhnk_research_tools.logger as logging

a = logging.get_logger(name="test_logger", level="INFO", format_short=True)

# logging.add_stdout_handler(logging.INFO)
# logger = logging.get_logger(level="DEBUG")

test_logger.VeryyLongClassNameThaWillbelong().my_method()

# import hhnk_research_tools.logger2 as logging

# logging.add_stdout_handler(logging.DEBUG)
