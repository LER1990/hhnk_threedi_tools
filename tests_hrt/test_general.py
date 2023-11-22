# %%
import pytest

from hhnk_research_tools.general_functions import dict_to_class


def test_dict_to_class():
    dummy_dict = {"a": 1, "b": {"c": 3}}

    # dot notation should raise an error
    with pytest.raises(AttributeError):
        dummy_dict.a

    # Convert to class and should now work
    dummy_class = dict_to_class(dummy_dict)
    assert dummy_class.b == {"c": 3}


if __name__ == "__main__":
    test_dict_to_class()
