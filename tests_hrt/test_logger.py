# %%
import sys

import hhnk_research_tools.logger as logging

# # logging.add_stdout_handler(logging.INFO)
logger = logging.get_logger(name=__name__, level=logging.DEBUG)


class A:
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def my_method(self):
        self.logger.info("hello from my method!")


class VeryyLongClassNameThaWillbelong:
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # self.logger = logging.get_logger(name=self.__class__)

    def my_method(self):
        self.logger.debug("hello from my method!")


# logger_promql_http_api = logging.getLogger('__name__.B')
# logger_promql_http_api.setLevel(logging.DEBUG)
# add_stdout_handler()

A().my_method()

b = VeryyLongClassNameThaWillbelong()
b.my_method()


# %%
