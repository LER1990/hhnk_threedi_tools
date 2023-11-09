import time

from threedi_api_client.openapi import ApiException


def call_threedi_api(func, max_retries=60, **kwargs):
    """add something to simulation, if apiexcetion is raised sleep on it and try again."""

    for i in range(max_retries):
        try:
            # check if data is dict
            if "data" in kwargs.keys():
                if type(kwargs["data"]) != dict:
                    print("OJEE... data is geen dict {func}")
                    break

            r = func(**kwargs)
            return r
        except ApiException as e:
            error = e
            print(e)
            if error.status == 400:
                print(f"ERROR in {func}")
                print(error.body)
                raise e
            else:  # TODO add error code of API overload
                time.sleep(10)
                continue
